"use strict"

var buttonSystemRequirement = document.getElementById('buttonSystemRequirement');
buttonSystemRequirement.addEventListener('click', openSystemRequirement, false);

var buttonCreateHardwareInfoFile = document.getElementById('buttonCreateHardwareInfoFile');
buttonCreateHardwareInfoFile.addEventListener('click', createHardwareInfoFile, false);

window.fusionJavaScriptHandler = {
    handle: function(action, data) {
        try {

            let obj = JSON.parse(data);

            if (action === 'updateHardwareInfo') {
                
                let tmp = '';
                let cpuname = obj.cpu.shortName[0];
                let cpuFreq = parseFloat(obj.cpu.frequency);
                let cpuCores = parseInt(obj.cpu.cores);
                let totalRamMemory = 0;

                let elemDiv = document.getElementById('hardwareInfo');

                // Debug
                if (obj.misc.debug) {
                    var elemP = document.createElement('p');
                    elemP.innerText = '/!\\ Debug /!\\'
                    elemDiv.appendChild(elemP);
                }

                // CPU
                var elemUl = document.createElement('ul');
                elemUl.className = 'custom-list';
                if (obj.cpu.count > 1 ) {
                    elemUl.innerText = `CPU (x${obj.cpu.count})`;
                } else {
                    elemUl.innerText = 'CPU';
                }
                // CPU name
                var elemLi = document.createElement('li');
                elemLi.id = 'none';
                elemLi.innerHTML = replaceSpecialChar(cpuname);
                elemUl.appendChild(elemLi);                
                // CPU frequency
                var elemLi = document.createElement('li');
                if ( cpuFreq < 1.7) {
                    elemLi.id = 'below';
                } else if ( cpuFreq < 3) {
                    elemLi.id = 'ok';
                } else {
                    elemLi.id = 'above';
                }
                elemLi.innerText = `${obj.cpu.frequency}GHz`;
                elemUl.appendChild(elemLi)
                // CPU cores/threads
                var elemLi = document.createElement('li');
                if ( cpuCores < 4) {
                    elemLi.id = 'below';
                } else if ( cpuCores < 6) {
                    elemLi.id = 'ok';
                } else {
                    elemLi.id = 'above';
                }  
                elemLi.innerText = `${obj.cpu.cores} cores / ${obj.cpu.threads} threads`;
                elemUl.appendChild(elemLi);
                
                elemDiv.appendChild(elemUl);

                // Debug
                if (obj.misc.debug) {
                    var elemP = document.createElement('p');
                    elemP.innerText = '/!\\ Debug /!\\'
                    elemDiv.appendChild(elemP);
                }
                
                // Memory
                var elemUl = document.createElement('ul');
                elemUl.className = 'custom-list';
                elemUl.innerText = 'Memory (RAM)';
                // Memory total
                for (var i=0; i<obj.memory.count; i++) {
                    totalRamMemory += parseInt(obj.memory.size[i], 10);
                }
                totalRamMemory /= 1024;
                var elemLi = document.createElement('li');
                if (totalRamMemory < 4) {
                    elemLi.id = 'below';
                } else if (totalRamMemory < 8) {
                    elemLi.id = 'ok';
                } else {
                    elemLi.id = 'above';
                }
                elemLi.innerText = `${totalRamMemory}GB`;
                elemUl.appendChild(elemLi);
                // Memory type
                if (obj.memory.type[0] != '')
                {
                    var elemLi = document.createElement('li');
                    elemLi.id = 'none';
                    elemLi.innerText = `${obj.memory.type[0]}`;
                    elemUl.appendChild(elemLi);  
                }  
                // Memory modules            
                for (var i=0;i<obj.memory.count;i++) {
                    var elemUl2 = document.createElement('ul');
                    elemUl2.className = 'custom-list2';
                    elemUl2.innerText = `Module #${i}`;
                    // Memory module size
                    var elemLi = document.createElement('li');
                    elemLi.id = 'none';
                    var memorySize = parseInt(obj.memory.size[i]);
                    if ( memorySize < 1024) {
                        elemLi.innerText = `${memorySize}MB`;
                    }
                    else {
                        memorySize /= 1024;
                        elemLi.innerText = `${memorySize}GB`;
                    }                    
                    elemUl2.appendChild(elemLi); 
                    // Memory module speed
                    if (obj.memory.speed[0] != '') {
                        var elemLi = document.createElement('li');
                        elemLi.id = 'none';
                        elemLi.innerText = `${obj.memory.speed[i]}MHz`;
                        elemUl2.appendChild(elemLi); 
                    }
                    elemUl.appendChild(elemUl2);
                }
                elemDiv.appendChild(elemUl);

                // Debug
                if (obj.misc.debug) {
                    var elemP = document.createElement('p');
                    elemP.innerText = '/!\\ Debug /!\\'
                    elemDiv.appendChild(elemP);
                }

                // GPU
                for (var i=0; i <obj.gpu.count; i++ ) {

                    var elemUl = document.createElement('ul');
                    elemUl.className = 'custom-list';
                    if (obj.gpu.count == 1)
                    {
                        elemUl.innerText = 'GPU';
                    } else {
                        elemUl.innerText = `GPU #${i}`;
                    }
                    // GPU name
                    var elemLi = document.createElement('li');
                    elemLi.id = 'none';
                    elemLi.innerHTML = replaceSpecialChar(obj.gpu.name[i]);
                    elemUl.appendChild(elemLi);   
                    // GPU memory
                    var elemLi = document.createElement('li');
                    var gpuMemory = parseInt(obj.gpu.memory[i]);
                    if (obj.gpu.type[i] === 'Discret') {
                        if (gpuMemory/1024 < 1) {
                            elemLi.id = 'below';
                        } else if (gpuMemory/1024 < 4) {
                            elemLi.id = 'ok';
                        } else {
                            elemLi.id = 'above';
                        }
                        if (gpuMemory < 1024) {
                            elemLi.innerText = `${gpuMemory}MB`;
                        }
                        else {
                            elemLi.innerText = `${gpuMemory/1024}GB`;
                        }                        
                    } else {
                        if (totalRamMemory < 6) {
                            elemLi.id = 'below';
                        } else {
                            elemLi.id = 'ok';
                        }
                        elemLi.innerText = `${totalRamMemory}GB (RAM)`;
                    }
                    elemUl.appendChild(elemLi); 
                    // GPU type
                    var elemLi = document.createElement('li');
                    elemLi.id = 'none';
                    elemLi.innerText = obj.gpu.type[i];
                    elemUl.appendChild(elemLi); 
                    elemDiv.appendChild(elemUl);            
                }               

                var elemHr = document.createElement('hr');
                elemDiv.appendChild(elemHr);

                // Legend
                var elemUl = document.createElement('ul');
                elemUl.className = 'custom-list';
                elemUl.innerText = 'Legend';
                // Legend below
                var elemLi = document.createElement('li');
                elemLi.id = 'below';
                elemLi.innerText = 'Below minimum requirements';
                elemUl.appendChild(elemLi);
                // Legend ok
                var elemLi = document.createElement('li');
                elemLi.id = 'ok';
                elemLi.innerText = 'Normal usage';
                elemUl.appendChild(elemLi);
                // Legend above
                var elemLi = document.createElement('li');
                elemLi.id = 'above';
                elemLi.innerText = 'Complex modelling or processing';
                elemUl.appendChild(elemLi);
                // Legend none
                var elemLi = document.createElement('li');
                elemLi.id = 'none';
                elemLi.innerText = 'No requirement';
                elemUl.appendChild(elemLi);
                elemDiv.appendChild(elemUl);

                document.getElementById('scanning').style.display = 'none';     
                
                buttonSystemRequirement.disabled = false;
                buttonCreateHardwareInfoFile.disabled = false;

            } else if (action==='sendText') {
                document.getElementById('test').innerHTML = obj.text;
            }						

        } catch (e) {

            console.log(e);
            console.log('exception caught with action: ' + action + ', data: ' + data);

            return 'FAILED';

        }

        return 'OK';
    }
};

function openSystemRequirement() {
    adsk.fusionSendData('openSystemRequirement', '');
}

function createHardwareInfoFile() {
    adsk.fusionSendData('createHardwareInfoFile', '');
}

function replaceSpecialChar(name) {

    name = name.replace('(R)', '&#174;');
    name = name.replace('(r)', '&#174;');
    name = name.replace('(TM)', '&#153;');
    name = name.replace('(tm)', '&#153;');

    return name;

}

window.onload = function () {
    var adskWaiter = setInterval(function () {
        console.log('wait for adsk object');
        if (window.adsk) {
            clearInterval(adskWaiter);
            adsk.fusionSendData('htmlLoaded', '');
        };
    }, 500);
}