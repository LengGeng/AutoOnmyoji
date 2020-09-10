function urlEncode(param, key, encode) {
    if (param == null) return '';
    let paramStr = '';
    let t = typeof (param);
    if (t === 'string' || t === 'number' || t === 'boolean') {
        paramStr += '&' + key + '=' + ((encode == null || encode) ? encodeURIComponent(param) : param);
    } else {
        for (let i in param) {
            if (!param.hasOwnProperty(i)) continue;
            let k = key == null ? i : key + (param instanceof Array ? '[]' : '.' + i);
            console.log(k);
            paramStr += urlEncode(param[i], k, encode);
        }
    }
    return paramStr;
}

function ajax(opts) {
    let defaultOpts = {
        url: '',            //ajax 请求地址
        type: 'GET',        //请求的方法,默认为GET
        data: null,         //请求的数据
        contentType: '',    //请求头
        dataType: 'json',   //请求的类型,默认为json
        async: true,        //是否异步，默认为true
        timeout: 5000,      //超时时间，默认5秒钟
        error: function () {
            console.log('error')
        },                  //错误执行的函数
        success: function () {
            console.log('success')
        }                   //请求成功的回调函数
    };

    for (let i in defaultOpts) {
        if (opts[i] === undefined) {
            opts[i] = defaultOpts[i];
        }
    }
    let xhr;
    if (window.XMLHttpRequest) {
        xhr = new XMLHttpRequest();
    } else {
        xhr = new ActiveXObject("Microsoft.XMLHTTP");
    }
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
            if (xhr.status === 200) {
                opts.success(xhr.responseText);
            } else {
                opts.error(xhr.status);
            }
        }
    };
    xhr.open(opts.type, opts.url, opts.async);
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhr.send(urlEncode(opts.data));
}

(function () {
    let deviceList = document.getElementById('device');
    let funsList = document.getElementById('funs');
    let argsList = document.getElementById('args');
    let run = document.getElementById('run');
    let screen = document.getElementById('screen');
    let screen_close = document.getElementById('screen-close');
    let re_device = document.getElementById('re-device');
    let screenImg = document.getElementsByClassName('screen-img')[0];

    re_device.onclick = getDevice;
    screen.onclick = getScreen;
    screen_close.onclick = screenClose;
    funsList.onchange = changeFuns;
    run.onclick = Run;

    let FUNS = [
        {
            name: "挑战",
            fun: "combat",
            args: ["请输入挑战的次数"],
            msg: "该功能用于正常的副本挑战,可适用于业原火、御灵、单人御魂、单人觉醒等场景。需要处于相应场景下,有该场景的挑战按钮。"
        },
        {
            name: "业原火",
            fun: "yeyuanhuo",
            args: ['请输入贪的数量', '请输入嗔的数量', '请输入痴的数量'],
            msg: "该功能用于业原火副本。可以选择贪嗔痴不同的挑战次数。需要处于庭院或业原火挑战界面。"
        },
        {
            name: "组队司机",
            fun: "zudui",
            args: ['请输入组队的次数'],
            msg: "该功能用于正常的组队挑战。可适应于组队御魂、觉醒等，需要先手动组队并勾选默认邀请。"
        },
        {
            name: "组队乘客",
            fun: "chengke",
            args: ['请输入组队的次数'],
            msg: "该功能用于正常的组队挑战。可适应于组队御魂、觉醒等，需要先勾选自动接收邀请。"
        },
        {
            name: "结界突破",
            fun: "jiejie",
            args: [],
            msg: "该功能用于结界突破。目前功能仍使用的老旧代码，请谨慎使用。"
        },
        {
            name: "万事屋自动领取",
            fun: "wanshiwu",
            args: [],
            msg: "该功能用于万事屋活动。用于自动领取奖励，需要处于庭院或万事屋主界面。"
        },
        {
            name: "超鬼王",
            fun: "chaoguiwang",
            args: [],
            msg: "该功能用于超鬼王活动。通过挑战单人觉醒刷超鬼王并自动击杀。需要预先配置好觉醒挑战层数和超鬼王阵容。" +
                "可能会因为网络波动而错过检测到超鬼王弹出界面，导致错过该超鬼王，并在该超鬼王存在期间持续挑战觉醒。"
        },
    ];

    function getDevice() {
        ajax({
            url: '/device',
            type: 'POST',
            success: function (responseText) {
                let response = JSON.parse(responseText);
                if (!response.code) {
                    let devices = response.data.devices;
                    let deviceHtml = '';
                    for (let device of devices) {
                        let id, status;
                        [id, status] = device;
                        if (status !== 'device') continue;
                        deviceHtml += `<option value="${id}">${id}</option>`;
                    }
                    deviceList.innerHTML = deviceHtml;
                }
            }
        });
    }

    function getScreen() {
        let device = deviceList.options[deviceList.selectedIndex].value;
        console.log(device);
        ajax({
            url: '/screen',
            type: 'POST',
            data: {device: device},
            success: function (responseText) {
                let response = JSON.parse(responseText);
                if (!response.code) {
                    screenImg.src = response.data.screen + '?date=' + new Date().getTime();
                    screenImg.style.display = 'block';
                }
            }
        });
    }

    function screenClose(e) {
        if (screenImg.getAttribute('src') === '') {
            console.log("截图不存在!");
            getScreen();
            return;
        }
        let close = e.target;
        if (close.innerText === '隐藏截图') {
            screenImg.style.display = 'none';
            close.innerText = '显示截图';
        } else if (close.innerText === '显示截图') {
            screenImg.style.display = 'block';
            close.innerText = '隐藏截图';
        }
    }

    function get_funs() {
        funsList.innerHTML = '';
        let funsHtml = '';
        FUNS.forEach(item => {
            funsHtml += `<option value="${item.fun}">${item.name}</option>`;
        });
        funsList.innerHTML = funsHtml;
        funsList.value = null;
    }

    function getActive() {
        console.log('获取活动任务!');
        let activeList = document.getElementsByClassName('active')[0];
        ajax({
            url: '/active',
            type: 'POST',
            success: function (responseText) {
                console.log(responseText);
                let response = JSON.parse(responseText);
                if (!response.code) {
                    let actives = response.data;
                    let activeHtml = '';
                    for (let active of actives) {
                        let device = active.device;
                        let fun = active.fun;
                        activeHtml += `<li><span>设备: ${device}</span><span>任务: ${fun}</span></li>`
                    }
                    activeList.innerHTML = activeHtml;
                }
            }
        });
    }

    function changeFuns(e) {
        let fun_active = e.target.value;
        FUNS.forEach(item => {
            let name, fun, args, msg;
            name = item.name;
            fun = item.fun;
            args = item.args;
            msg = item.msg;
            if (fun_active === fun) {
                let argsHtml = `<p>${msg}</p>`;
                if (args.length) {
                    argsList.innerHTML = '';
                    for (let i in args) {
                        if (!args.hasOwnProperty(i)) continue;
                        argsHtml += `<input name="args[${i}]" type="number" placeholder="${args[i]}">`;
                    }
                    argsList.innerHTML = argsHtml;
                } else {
                    argsList.innerHTML = argsHtml + "该功能不使用参数!";
                }
            }
        });
    }

    function Run() {
        // 获取选择的设备
        let device = deviceList.value;
        // 获取选择的功能
        let fun = funsList.value;
        // 获取参数列表
        let argsArray = argsList.getElementsByTagName('input');
        console.log(argsArray);
        let args = [];
        if (argsArray.length) {
            [].forEach.call(argsArray, input => {
                args.push((isNaN(input.value) || input.value === '') ? 0 : parseInt(input.value));
            })
        }

        let data = {device: device, fun: fun, args: args};
        console.log(data);
        ajax({
            url: '/run',
            type: 'POST',
            data: data,
            success: function (responseText) {
                let response = JSON.parse(responseText);
                if (!response.code) {
                    alert("任务以执行");
                    getActive();
                } else if (response.code === 1001) {
                    alert(response.msg);
                }
            }
        });
    }

    getDevice();
    get_funs();
    setInterval(function () {
        console.log("测试重复执行");
        getActive();
    }, 1000 * 60);
})();