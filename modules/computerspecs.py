import platform
import subprocess
import json
import os

# For debugging purpose only
debugMode = True
fileFromOs = ''
if platform.system() == 'Windows':
    txtFile = os.path.join(os.getenv('USERPROFILE'), 'Desktop', 'HMFusion360', '01', 'HMFusion360.txt')
else:
    txtFile = os.path.join(os.path.expanduser('~'), 'Desktop', 'HMFusion360.txt')

hardwareInfo = {'cpu': {'longName': [],
                        'shortName': [],
                        'count': -1,
                        'cores': -1,
                        'threads': -1,
                        'frequency': -1},
                'gpu': {'name': [],
                        'count': -1,
                        'memory': [],
                        'type': []},
                'memory': {'count': -1,
                            'size': [],
                            'speed': [],
                            'type': []},
                'misc': {'debug': debugMode}
                }


def getHardwareInfo():

    hardwareInfo['misc']['debug'] = False

    flag = getCpuInfo() & getMemoryInfo() & getGpuInfo()

    checkCollectedInfo()

    return hardwareInfo, flag


def getHardwareInfoFromFile():

    hardwareInfo['misc']['debug'] = True

    flag = readHardwareInfoFile()

    checkCollectedInfo()

    return hardwareInfo, flag


def shortenCpuName():

    global hardwareInfo

    try:

        for name in hardwareInfo['cpu']['longName']:
            # Remove multiple spaces inside string
            shortCpuName = ' '.join(name.split())

            if shortCpuName.startswith('Intel(R) Core(TM)'):

                # 'Intel(R) Core(TM) i7-3770K CPU @ 3.50GHz'
                shortCpuName = shortCpuName.split(' CPU @')[0]

            elif shortCpuName.startswith('Intel(R) Xeon(TM)'):

                # 'Intel(R) Xeon(TM) CPU E5-2670 0 @ 2.60GHz'
                shortCpuName = shortCpuName.split(' @')[0]
                shortCpuName = shortCpuName.replace(' CPU', '')

            else:

                # AMD processors (mostly)
                shortCpuName = shortCpuName.replace(' Dual-Core Processor', '')
                shortCpuName = shortCpuName.replace(' Quad-Core Processor', '')
                shortCpuName = shortCpuName.replace(' 4-Core Processor', '')
                shortCpuName = shortCpuName.replace(' 6-Core Processor', '')
                shortCpuName = shortCpuName.replace(' 8-Core Processor', '')
                shortCpuName = shortCpuName.replace(' 12-Core Processor', '')
                shortCpuName = shortCpuName.replace(' 16-Core Processor', '')

            hardwareInfo['cpu']['shortName'].append(shortCpuName)

        return True

    except:

        return False


def checkCollectedInfo():

    if not hardwareInfo['misc']['debug']:
        if platform.system() == 'Windows':
            checkWindowsInfo()
        else:
            checkMacOsInfo()
    else:
        if fileFromOs == 'windows':
            checkWindowsInfo()
        else:
            checkMacOsInfo()


def checkWindowsInfo():

    # Convert CPU frequency from MHz to GHz
    hardwareInfo['cpu']['frequency'] = '{:.2f}'.format(int(hardwareInfo['cpu']['frequency'])/1000)

    for i in range(0, hardwareInfo['memory']['count']):
        # Convert memory module size from Bytes to Megabytes
        hardwareInfo['memory']['size'][i] = '{}'.format(int(hardwareInfo['memory']['size'][i])//1024//1024)
        # Convert memory module type
        hardwareInfo['memory']['type'][i] = hardwareInfo['memory']['type'][i].replace('24', 'DDR3').replace('0','DDR4')
        if hardwareInfo['memory']['type'][i] not in ['DDR3', 'DDR4']:
            hardwareInfo['memory']['type'][i] = ''

    for i in range(0, hardwareInfo['gpu']['count']):
        # Convert gpu memory size from Bytes to Megabytes
        hardwareInfo['gpu']['memory'][i] = '{}'.format(int(hardwareInfo['gpu']['memory'][i])//1024//1024)

    shortenCpuName()


def checkMacOsInfo():

    # Remove unit from CPU frequency
    hardwareInfo['cpu']['frequency'] = hardwareInfo['cpu']['frequency'].replace('GHz', '').replace(',', '.').strip()

    for i in range(0, hardwareInfo['memory']['count']):
        # Remove unit from memory module size
        hardwareInfo['memory']['size'][i] = hardwareInfo['memory']['size'][i].replace('GB', '').strip()
        hardwareInfo['memory']['size'][i] = '{}'.format(int(hardwareInfo['memory']['size'][i]) * 1024)
        # Remove unit from memory speed
        hardwareInfo['memory']['speed'][i] = hardwareInfo['memory']['speed'][i].replace('MHz', '').strip()

    for i in range(0, hardwareInfo['gpu']['count']):
        # Convert gpu memory size from Gygobytes to Megabytes
        hardwareInfo['gpu']['memory'][i] = hardwareInfo['gpu']['memory'][i].replace(' MB', '')

    shortenCpuName()


def getCpuInfo():

    global hardwareInfo

    try:

        if platform.system() == 'Windows':

            tmp = subprocess.getoutput('wmic cpu get Name,NumberOfCores,NumberOfLogicalProcessors,MaxClockSpeed /value').strip().split('\n')
            tmp = [x for x in tmp if x != '']

            count = 0
            for t in tmp:
                if t.startswith('MaxClockSpeed='):
                    hardwareInfo['cpu']['frequency'] = t.replace('MaxClockSpeed=', '')
                elif t.startswith('Name='):
                    hardwareInfo['cpu']['longName'].append(t.replace('Name=', ''))
                    count += 1
                elif t.startswith('NumberOfCores='):
                    hardwareInfo['cpu']['cores'] = t.replace('NumberOfCores=', '')
                elif t.startswith('NumberOfLogicalProcessors='):
                    hardwareInfo['cpu']['threads'] = t.replace('NumberOfLogicalProcessors=', '')

            hardwareInfo['cpu']['count'] = count

        else:

            temp = subprocess.getoutput('sysctl machdep.cpu').split('\n')
            hardwareInfo['cpu']['longName'] = [x.replace('machdep.cpu.brand_string:', '').strip() for x in temp if x.startswith('machdep.cpu.brand_string')]
            hardwareInfo['cpu']['count']  = len(hardwareInfo['cpu']['longName'])
            hardwareInfo['cpu']['cores'] = [x.replace('machdep.cpu.core_count:', '').strip() for x in temp if x.startswith('machdep.cpu.core_count')]
            hardwareInfo['cpu']['threads'] = [x.replace('machdep.cpu.thread_count:', '').strip() for x in temp if x.startswith('machdep.cpu.thread_count')]

            tmp = subprocess.getoutput('system_profiler -json SPHardwareDataType')
            tmp = json.loads(tmp)
            hardwareInfo['cpu']['frequency'] = tmp['SPHardwareDataType'][0]['current_processor_speed']

        return True

    except:

        return False


def getMemoryInfo():

    global hardwareInfo

    try:

        if platform.system() == 'Windows':

            tmp = subprocess.getoutput('wmic memorychip get Capacity,Speed,MemoryType /value').strip().split('\n')
            tmp = [x for x in tmp if x != '']

            for t in tmp:
                if t.startswith('Capacity='):
                    hardwareInfo['memory']['size'].append(t.replace('Capacity=', ''))
                elif t.startswith('Speed='):
                    hardwareInfo['memory']['speed'].append(t.replace('Speed=', ''))
                elif t.startswith('MemoryType='):
                    hardwareInfo['memory']['type'].append(t.replace('MemoryType=', ''))

            hardwareInfo['memory']['count'] = len(hardwareInfo['memory']['size'])

        else:

            tmp = subprocess.getoutput('system_profiler -json SPMemoryDataType')
            tmp = json.loads(tmp)

            hardwareInfo['memory']['count'] = len(tmp['SPMemoryDataType'][0]['_items'])

            for i in range(0, hardwareInfo['memory']['count']):
                hardwareInfo['memory']['size'].append(tmp['SPMemoryDataType'][0]['_items'][i]['dimm_size'].strip())
                hardwareInfo['memory']['speed'].append(tmp['SPMemoryDataType'][0]['_items'][i]['dimm_speed'].strip())
                hardwareInfo['memory']['type'].append(tmp['SPMemoryDataType'][0]['_items'][i]['dimm_type'].strip())

        return True

    except:

        return False


def getGpuInfo():

    global hardwareInfo

    try:

        if platform.system() == 'Windows':
            tmp = subprocess.getoutput('wmic path Win32_VideoController get AdapterRAM,Name /value').strip().split('\n')
            tmp = [x for x in tmp if x != '']
            count = 0
            for t in tmp:
                if t.startswith('Name='):
                    hardwareInfo['gpu']['name'].append(t.replace('Name=', ''))
                    if hardwareInfo['gpu']['name'][count].startswith('NVIDIA') or hardwareInfo['gpu']['name'][count].startswith('AMD'):
                        hardwareInfo['gpu']['type'].append('Discret')
                    else:
                        hardwareInfo['gpu']['type'].append('Integrated')
                    count += 1
                elif t.startswith('AdapterRAM='):
                    hardwareInfo['gpu']['memory'].append(t.replace('AdapterRAM=', ''))
            hardwareInfo['gpu']['count'] = count
        else:
            tmp = subprocess.getoutput('system_profiler SPDisplaysDataType').strip().split('\n')
            tmp = [x.strip() for x in tmp if x != '']
            count = 0
            for t in tmp:
                if t.startswith('Chipset Model: '):
                    hardwareInfo['gpu']['name'].append(t.replace('Chipset Model: ', ''))
                    count += 1
                elif t.startswith('Bus: '):
                    hardwareInfo['gpu']['type'].append(t.replace('Bus: ', '').replace('Built-In', 'Integrated').replace('PCIe', 'Discret'))
                elif t.startswith('VRAM (Dynamic, Max): '):
                    hardwareInfo['gpu']['memory'].append('')
                elif t.startswith('VRAM (Total): '):
                    hardwareInfo['gpu']['memory'].append(t.replace('VRAM (Total): ', ''))
            hardwareInfo['gpu']['count'] = count

        return True

    except:

        return False


def collectHardwareInfo():

    try:

        if platform.system() == 'Windows':

            desktopPath = os.path.join(os.getenv('USERPROFILE'), 'Desktop', 'HMFusion360.txt')

            subprocess.run(['wmic', 'cpu', 'get', '/value',  '>', desktopPath], shell=True)
            subprocess.run(['wmic', 'path', 'Win32_VideoController', 'get', '/value', '>>',  desktopPath], shell=True)
            subprocess.run(['wmic', 'memorychip', 'get', '/value', '>>', desktopPath], shell=True)

        else:

            desktopPath = os.path.join(os.path.expanduser('~'), 'Desktop', 'HMFusion360.txt')

            with open(desktopPath, 'w') as f:
                tmp = subprocess.getoutput('sysctl machdep.cpu')
                f.write(tmp)
                f.write('\n\n----\n\n')
                tmp = subprocess.getoutput('system_profiler SPHardwareDataType SPDisplaysDataType SPMemoryDataType')
                f.write(tmp)
                f.write('\n\n----\n\n')
                tmp = subprocess.getoutput('system_profiler -json SPHardwareDataType SPDisplaysDataType SPMemoryDataType')
                f.write(tmp)
                f.write('\n\n')

        return True

    except:

        return False


def readHardwareInfoFile():

    try:

        global fileFromOs

        if not os.path.exists(txtFile):
            # TODO
            print('File not found')
            return False

        with open(txtFile, 'r') as f:
            lines = f.readlines()
            for line in lines:
                line = line.replace('\0', '').strip()
                if line == '':
                    continue
                if line.startswith('AddressWidth='):
                    fileFromOs = 'windows'
                    break
                if line.startswith('machdep.cpu'):
                    fileFromOs = 'macos'
                    break

        if fileFromOs == 'windows':
            flag = parseWindowsFile()

        elif fileFromOs == 'macos':
            flag = parseMacOsFile()
        else:
            flag = False

        return flag

    except:

        return False


def parseWindowsFile():

    try:

        hardwareInfo['cpu']['count'] = 0
        hardwareInfo['gpu']['count'] = 0
        hardwareInfo['memory']['count'] = 0

        with open(txtFile, 'r') as f:

            lines = f.readlines()

        for line in lines:

            line = line.replace('\0', '').strip()
            if line == '':
                continue

            if line.startswith('AddressWidth='):
                deviceType = 'cpu'
                hardwareInfo['cpu']['count'] += 1
            elif line.startswith('AcceleratorCapabilities='):
                deviceType = 'gpu'
                hardwareInfo['gpu']['count'] += 1
            elif line.startswith('BankLabel='):
                deviceType = 'memory'
                hardwareInfo['memory']['count'] += 1

            # CPU
            if line.startswith('MaxClockSpeed=') and deviceType == 'cpu':
                hardwareInfo['cpu']['frequency'] = line.replace('MaxClockSpeed=', '')
            elif line.startswith('Name=') and deviceType == 'cpu':
                hardwareInfo['cpu']['longName'].append(line.replace('Name=', ''))
            elif line.startswith('NumberOfCores=') and deviceType == 'cpu':
                hardwareInfo['cpu']['cores'] = line.replace('NumberOfCores=', '')
            elif line.startswith('NumberOfLogicalProcessors=') and deviceType == 'cpu':
                hardwareInfo['cpu']['threads'] = line.replace('NumberOfLogicalProcessors=', '')
            # GPU
            elif line.startswith('Name=') and deviceType == 'gpu':
                hardwareInfo['gpu']['name'].append(line.replace('Name=', ''))
                if hardwareInfo['gpu']['name'][-1].startswith('NVIDIA') or hardwareInfo['gpu']['name'][-1].startswith('AMD'):
                    hardwareInfo['gpu']['type'].append('Discret')
                else:
                    hardwareInfo['gpu']['type'].append('Integrated')
            elif line.startswith('AdapterRAM=') and deviceType == 'gpu':
                hardwareInfo['gpu']['memory'].append(line.replace('AdapterRAM=', ''))
            # Memory
            elif line.startswith('Capacity=') and deviceType == 'memory':
                hardwareInfo['memory']['size'].append(line.replace('Capacity=', ''))
            elif line.startswith('Speed=') and deviceType == 'memory':
                hardwareInfo['memory']['speed'].append(line.replace('Speed=', ''))
            elif line.startswith('MemoryType=') and deviceType == 'memory':
                hardwareInfo['memory']['type'].append(line.replace('MemoryType=', ''))

        return True

    except:

        return False


def splitMacOsFile():

    path = os.path.dirname(txtFile)

    with open(txtFile, 'r') as f:
        txt = f.read()

    txtChuncks = txt.split('----')

    macdepFile = os.path.join(path, 'HMFusion360Machdep.txt')
    with open(macdepFile, 'w') as f:
        f.write(txtChuncks[0])
    systemProfilerFile = os.path.join(path, 'HMFusion360Systemprofiler.txt')
    with open(systemProfilerFile, 'w') as f:
        f.write(txtChuncks[1])
    systemProfilerJsonFile = os.path.join(path, 'HMFusion360Systemprofiler.json')
    with open(systemProfilerJsonFile, 'w') as f:
        f.write(txtChuncks[2])

    return macdepFile, systemProfilerFile, systemProfilerJsonFile


def parseMacOsFile():

    try:

        macdepFile, systemProfilerFile, systemProfilerJsonFile = splitMacOsFile()

        with open(macdepFile, 'r') as file:
            lines = file.readlines()
            for line in lines:
                if line.startswith('machdep.cpu.brand_string'):
                    hardwareInfo['cpu']['longName'].append(line.replace('machdep.cpu.brand_string:', '').strip())
                if line.startswith('machdep.cpu.core_count'):
                    hardwareInfo['cpu']['cores'] = line.replace('machdep.cpu.core_count:', '').strip()
                if line.startswith('machdep.cpu.thread_count'):
                    hardwareInfo['cpu']['threads'] = line.replace('machdep.cpu.thread_count:', '').strip()

        hardwareInfo['cpu']['count'] = len(hardwareInfo['cpu']['longName'])

        with open(systemProfilerJsonFile, 'r') as file:
                    tmp = json.load(file)

        hardwareInfo['cpu']['frequency'] = tmp['SPHardwareDataType'][0]['current_processor_speed']

        hardwareInfo['memory']['count'] = len(tmp['SPMemoryDataType'][0]['_items'])

        for i in range(0, hardwareInfo['memory']['count']):
            hardwareInfo['memory']['size'].append(tmp['SPMemoryDataType'][0]['_items'][i]['dimm_size'].strip())
            hardwareInfo['memory']['speed'].append(tmp['SPMemoryDataType'][0]['_items'][i]['dimm_speed'].strip())
            hardwareInfo['memory']['type'].append(tmp['SPMemoryDataType'][0]['_items'][i]['dimm_type'].strip())

        hardwareInfo['gpu']['count'] = len(tmp['SPDisplaysDataType'])
        for i in range(0, hardwareInfo['gpu']['count']):
            hardwareInfo['gpu']['name'].append(tmp['SPDisplaysDataType'][i]['sppci_model'])
            if tmp['SPDisplaysDataType'][i]['sppci_bus'].endswith('_builtin'):
                hardwareInfo['gpu']['type'].append('Integrated')
            else:
                hardwareInfo['gpu']['type'].append('Discret')
            hardwareInfo['gpu']['memory'].append(tmp['SPDisplaysDataType'][i]['_spdisplays_vram'])

        return True

    except:

        return False


if __name__ == '__main__':

    if not hardwareInfo['misc']['debug']:
        hardwareInfo, flag = getHardwareInfo()
    else:
        hardwareInfo, flag = getHardwareInfoFromFile()

    if flag:

        if hardwareInfo['misc']['debug']:
            print('\n/!\\ DEBUG MODE /!\\')

        if hardwareInfo['cpu']['count']==1:
            print('\nCPU')
        else:
            print('\nCPU (x{})'.format(hardwareInfo['cpu']['count']))
        print('\tLong name: {}'.format(hardwareInfo['cpu']['longName'][0]))
        print('\tShort name: {}'.format(hardwareInfo['cpu']['shortName'][0]))
        print('\tFrequency: {}GHz'.format(hardwareInfo['cpu']['frequency']))
        print('\tCores/Threads: {} / {}'.format(hardwareInfo['cpu']['cores'], hardwareInfo['cpu']['threads']))

        if hardwareInfo['misc']['debug']:
            print('\n/!\\ DEBUG MODE /!\\')

        print('\nMemory (RAM)')

        totalMemory = 0
        for m in hardwareInfo['memory']['size']:
            totalMemory += int(m)
        if totalMemory < 1024:
            print('\tTotal: {}MB'.format(totalMemory))
        else:
            print('\tTotal: {}GB'.format(totalMemory//1024))
        if hardwareInfo['memory']['type'][0] == '':
            print('\tType: N/A')
        else:
            print('\tType: {}'.format(hardwareInfo['memory']['type'][0]))
        for i in range(0, hardwareInfo['memory']['count']):
            print('\tModule #{}'.format(i))
            if int(hardwareInfo['memory']['size'][i]) < 1024:
                print('\t\tSize: {}MB'.format(hardwareInfo['memory']['size'][i]))
            else:
                print('\t\tSize: {}GB'.format(int(hardwareInfo['memory']['size'][i])//1024))
            if hardwareInfo['memory']['speed'][0] == '':
                print('\t\tSpeed: N/A')
            else:
                print('\t\tSpeed: {}MHz'.format(hardwareInfo['memory']['speed'][i]))

        if hardwareInfo['misc']['debug']:
            print('\n/!\\ DEBUG MODE /!\\')

        for i in range(0, hardwareInfo['gpu']['count']):
            if hardwareInfo['gpu']['count'] == 1:
                print('\nGPU')
            else:
                print('\nGPU #{}'.format(i))
            print('\tName: {}'.format(hardwareInfo['gpu']['name'][i]))
            if hardwareInfo['gpu']['type'][i] == 'Discret':
                if int(hardwareInfo['gpu']['memory'][i]) < 1024:
                    print('\tMemory: {}MB'.format(hardwareInfo['gpu']['memory'][i]))
                else:
                    print('\tMemory: {}GB'.format(int(hardwareInfo['gpu']['memory'][i])//1024))
            else:
                if totalMemory < 1024:
                    print('\tMemory: {}MB (RAM)'.format(totalMemory))
                else:
                    print('\tMemory: {}GB (RAM)'.format(totalMemory//1024))
            print('\tType: {}'.format(hardwareInfo['gpu']['type'][i]))

        if hardwareInfo['misc']['debug']:
            print('\n/!\\ DEBUG MODE /!\\')

    else:

        if hardwareInfo['misc']['debug']:
            print('\n/!\\ DEBUG MODE /!\\')

        print('An error occured.\n')
        print('Data collectd so far:\n')
        print(hardwareInfo)

        if hardwareInfo['misc']['debug']:
            print('\n/!\\ DEBUG MODE /!\\')
