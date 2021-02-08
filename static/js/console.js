//插件
(function () {
    /*
     * logEl 输出的容器element
     * isInitialized 是否初始化
     * _console
     */
    var logEl,
        isInitialized = false,
        _console = {};

    /*
     * 创建元素
     * tag 标签名称
     * css 样式
     */
    function createElement( tag, css ) {
        var element = document.createElement( tag );
        element.style.cssText = css;
        return element;
    }

    /*
     * 生成面板
     * options 自定义样式对象
     */
    function createPanel(options) {
        options.bgColor = options.bgColor || 'black';
        options.color = options.color || 'lightgreen';
        options.css = options.css || '';
        var div = createElement( 'div', 'font-family:Helvetica,Arial,sans-serif;font-size:10px;font-weight:bold;padding:5px;text-align:left;opacity:0.8;position:fixed;right:0;top:0;min-width:200px;max-height:50vh;overflow:auto;margin-top:100px;background:' + options.bgColor + ';color:' + options.color + ';' + options.css);
        return div;
    }

    /*
     * 日志信息，自定义log方法
     */
    function log() {
        var el = createElement( 'div', 'line-height:18px;background:' + (logEl.children.length % 2 ? 'rgba(255,255,255,0.2)' : '')); // zebra lines
        var val = [].slice.call(arguments).reduce(function(prev, arg) {//
            return prev + ' ' + arg;
        }, '');
        el.textContent = val;

        logEl.appendChild(el);
        // Scroll to last element
        logEl.scrollTop = logEl.scrollHeight - logEl.clientHeight;
    }

    /*
     * 清空控制台
     */
    function clear() {
        logEl.innerHTML = '';
    }

    /*
     * 初始化插件，可以添加附加选项
     */
    function init(options){
        if (isInitialized) { return; }

        isInitialized = true;
        options = options || {};
        logEl = createPanel(options);
        document.body.appendChild(logEl);

        if (!options.freeConsole) {
            // 同步打印更新
            _console.log = console.log;
            _console.clear = console.clear;

            console.log = originalFnCallDecorator(log, 'log');
            console.clear = originalFnCallDecorator(clear, 'clear');
        }
    }

    /*
     * 销毁插件并恢复原来的控制台显示
     */
    function destroy() {
        isInitialized = false;
        console.log = _console.log;
        console.clear = _console.clear;
        logEl.remove();
    }

    /*
     * 验证初始化
     */
    function checkInitialized(){
        if (!isInitialized){
            throw 'You need to call `screenLog.init()` first.';
        }
    }

    function checkInitDecorator(fn){
        return function(){
            checkInitialized();
            return fn.apply(this, arguments);
        };
    }

    /*
     * 包含前台打印和后台打印
     */
    function originalFnCallDecorator(fn, fnName) {
        return function(){
            //前台打印
            fn.apply(this, arguments);
            if (typeof _console[fnName] === 'function') {
                //后台打印
                _console[fnName].apply(console, arguments);
            }
        };
    }

    window.screenLog = {
        init: init,
        log: originalFnCallDecorator(checkInitDecorator(log), 'log'),
        clear: originalFnCallDecorator(checkInitDecorator(clear), 'clear'),
        destroy: checkInitDecorator(destroy)
    };
})();


