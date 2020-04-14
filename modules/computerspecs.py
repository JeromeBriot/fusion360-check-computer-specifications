import platform
import subprocess
import json
import os

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
                            'type': []}
                }


def getHardwareInfo():

    flag = getCpuInfo() & getMemoryInfo() & getGpuInfo()
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


def getCpuInfo():

    global hardwareInfo

    try:

        if platform.system() == 'Windows':

            tmp = subprocess.getoutput('wmic cpu get Name,NumberOfCores,NumberOfLogicalProcessors,MaxClockSpeed /value').strip().split('\n')
            tmp = [x for x in tmp if x != '']

            count = 0
            for t in tmp:
                if t.startswith('MaxClockSpeed='):
                    hardwareInfo['cpu']['frequency'] = '{:.2f}'.format(int(t.replace('MaxClockSpeed=', ''))/1000)
                elif t.startswith('Name='):
                    hardwareInfo['cpu']['longName'].append(t.replace('Name=', ''))
                    count += 1
                elif t.startswith('NumberOfCores='):
                    hardwareInfo['cpu']['cores'] = t.replace('NumberOfCores=', '')
                elif t.startswith('NumberOfLogicalProcessors='):
                    hardwareInfo['cpu']['threads'] = t.replace('NumberOfLogicalProcessors=', '')

            hardwareInfo['cpu']['count'] = count

            shortenCpuName()

        else:

            temp = subprocess.getoutput('sysctl machdep.cpu').split('\n')
            hardwareInfo['cpu']['longName'] = [x.replace('machdep.cpu.brand_string:', '').strip() for x in temp if x.startswith('machdep.cpu.brand_string')]
            hardwareInfo['cpu']['count']  = len(hardwareInfo['cpu']['longName'])
            hardwareInfo['cpu']['cores'] = [x.replace('machdep.cpu.core_count:', '').strip() for x in temp if x.startswith('machdep.cpu.core_count')]
            hardwareInfo['cpu']['threads'] = [x.replace('machdep.cpu.thread_count:', '').strip() for x in temp if x.startswith('machdep.cpu.thread_count')]

            tmp = subprocess.getoutput('system_profiler -json SPHardwareDataType')
            tmp = json.loads(tmp)
            hardwareInfo['cpu']['frequency'] = tmp['SPHardwareDataType'][0]['current_processor_speed'].replace('GHz', '').replace(',', '.').strip()

            shortenCpuName()

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
                    hardwareInfo['memory']['size'].append('{}'.format(int(t.replace('Capacity=', ''))//1024//1024//1024))
                elif t.startswith('Speed='):
                    hardwareInfo['memory']['speed'].append(t.replace('Speed=', ''))
                elif t.startswith('MemoryType='):
                    hardwareInfo['memory']['type'].append(t.replace('MemoryType=', '').replace('24', 'DDR3').replace('0','DDR4'))

            hardwareInfo['memory']['count'] = len(hardwareInfo['memory']['size'])

        else:

            tmp = subprocess.getoutput('system_profiler -json SPMemoryDataType')
            tmp = json.loads(tmp)

            hardwareInfo['memory']['count'] = len(tmp['SPMemoryDataType'][0]['_items'])

            for i in range(0, hardwareInfo['memory']['count']):
                hardwareInfo['memory']['size'].append(tmp['SPMemoryDataType'][0]['_items'][i]['dimm_size'].replace('GB', '').strip())
                hardwareInfo['memory']['speed'].append(tmp['SPMemoryDataType'][0]['_items'][i]['dimm_speed'].replace('MHz', '').strip())
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
                    hardwareInfo['gpu']['memory'].append('{}'.format(int(t.replace('AdapterRAM=', ''))//1024//1024//1024))
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
                    hardwareInfo['gpu']['memory'].append('{}'.format(int(int(t.replace('VRAM (Total): ', '').replace(' MB', ''))/1024)))
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
                f.write('\n')
                tmp = subprocess.getoutput('system_profiler SPHardwareDataType')
                f.write(tmp)
                f.write('\n')
                tmp = subprocess.getoutput('system_profiler -json SPHardwareDataType')
                f.write(tmp)
                f.write('\n\n')
                tmp = subprocess.getoutput('system_profiler SPDisplaysDataType')
                f.write(tmp)
                f.write('\n')
                tmp = subprocess.getoutput('system_profiler -json SPDisplaysDataType')
                f.write(tmp)
                f.write('\n\n')
                tmp = subprocess.getoutput('system_profiler SPMemoryDataType')
                f.write(tmp)
                f.write('\n')
                tmp = subprocess.getoutput('system_profiler -json SPMemoryDataType')
                f.write(tmp)

        return True

    except:

        return False


if __name__ == '__main__':

    hardwareInfo, flag = getHardwareInfo()

    if flag:

        if hardwareInfo['cpu']['count']==1:
            print('\nCPU')
        else:
            print('\nCPU (x{})'.format(hardwareInfo['cpu']['count']))
        print('\tLong name: {}'.format(hardwareInfo['cpu']['longName'][0]))
        print('\tShort name: {}'.format(hardwareInfo['cpu']['shortName'][0]))
        print('\tFrequency: {}GHz'.format(hardwareInfo['cpu']['frequency']))
        print('\tCores/Threads: {} / {}'.format(hardwareInfo['cpu']['cores'], hardwareInfo['cpu']['threads']))

        print('\nMemory (RAM)')

        totalMemory = 0
        for m in hardwareInfo['memory']['size']:
            totalMemory += int(m)
        print('\tTotal: {}GB'.format(totalMemory))
        print('\tType: {}'.format(hardwareInfo['memory']['type'][0]))
        for i in range(0, hardwareInfo['memory']['count']):
            print('\tModule #{}'.format(i))
            print('\t\tSize: {}GB'.format(hardwareInfo['memory']['size'][i]))
            print('\t\tSpeed: {}MHz'.format(hardwareInfo['memory']['speed'][i]))


        for i in range(0, hardwareInfo['gpu']['count']):
            if hardwareInfo['gpu']['count'] == 1:
                print('\nGPU')
            else:
                print('\nGPU #{}'.format(i))
            print('\tName: {}'.format(hardwareInfo['gpu']['name'][i]))
            if hardwareInfo['gpu']['type'][i] == 'Discret':
                print('\tMemory: {}GB'.format(hardwareInfo['gpu']['memory'][i]))
            else:
                print('\tMemory: {}GB (RAM)'.format(totalMemory))
            print('\tType: {}'.format(hardwareInfo['gpu']['type'][i]))

    else:
        print('An error occured.\n')
        print('Data collectd so far:\n')
        print(hardwareInfo)

