#Author-Jerome Briot
#Description-Check the computer specifications against recommended requirements by Autodesk.

import adsk.core, adsk.fusion, traceback # pylint: disable=import-error
import json
import threading
import webbrowser
from .modules import computerspecs

thisAddinName = 'CheckComputerSpecs'
thisAddinTitle = 'Check Computer Specs'
thisAddinVersion = '0.1.0'
thisAddinAuthor = 'Jerome Briot'
thisAddinContact = 'jbtechlab@gmail.com'

app = adsk.core.Application.cast(None)
ui = adsk.core.UserInterface.cast(None)
palette = adsk.core.Palette.cast(None)

useNewWebBrowser = True

handlers = []

myCustomEventId = thisAddinName + 'customEvent'
myCustomEvent = None
stopFlag = None
myThread = None

timeoutBeforeSendingData = 1

class ShowPaletteCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):

        try:

            palette = ui.palettes.itemById(thisAddinName + 'Palette')

            if not palette:
                palette = ui.palettes.add(thisAddinName + 'Palette', thisAddinTitle, thisAddinName + '.html', True, True, True, 250, 750, useNewWebBrowser)

                onHTMLEvent = MyHTMLEventHandler()
                palette.incomingFromHTML.add(onHTMLEvent)
                handlers.append(onHTMLEvent)

            else:
                palette.isVisible = not(palette.isVisible)

        except:
            ui.messageBox('Command executed failed: {}'.format(traceback.format_exc()), thisAddinName, 0, 0)


class ShowPaletteCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        global handlers
        try:
            command = args.command
            onExecute = ShowPaletteCommandExecuteHandler()
            command.execute.add(onExecute)
            handlers.append(onExecute)
        except:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()), thisAddinName, 0, 0)


# Event handler for the palette HTML event.
class MyHTMLEventHandler(adsk.core.HTMLEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):

        try:

            htmlArgs = adsk.core.HTMLEventArgs.cast(args)            

            if useNewWebBrowser and htmlArgs.action == 'response':
                dataFromHtml = json.loads(htmlArgs.data)
                if dataFromHtml['data'] != 'OK':
                    ui.messageBox('Failed:\nPalette object reurns an error.')
            elif htmlArgs.action == 'htmlLoaded':
                myThread.start()
            elif htmlArgs.action == 'openSystemRequirement':
                webbrowser.open('https://knowledge.autodesk.com/support/fusion-360/troubleshooting/caas/sfdcarticles/sfdcarticles/System-requirements-for-Autodesk-Fusion-360.html')
            elif htmlArgs.action == 'createHardwareInfoFile':  
                computerspecs.collectHardwareInfo()

        except:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# The event handler that responds to the custom event being fired.
class ThreadEventHandler(adsk.core.CustomEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:

            hardwareInfo, flag = computerspecs.getHardwareInfo()

            if flag:

                palette = ui.palettes.itemById(thisAddinName + 'Palette')

                if palette:
                    if useNewWebBrowser:
                        palette.sendInfoToHTML('updateHardwareInfo', json.dumps(hardwareInfo))
                    else:
                        response = palette.sendInfoToHTML('updateHardwareInfo', json.dumps(hardwareInfo))
                        if response != 'OK':
                            ui.messageBox('Failed:\nPalette object reurns an error.')
            else:

                ui.messageBox('Failed:\nUnable to scan hatdware.')

        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


class MyThread(threading.Thread):
    def __init__(self, event):
        threading.Thread.__init__(self)
        self.stopped = event

    def run(self):
        while not self.stopped.wait(timeoutBeforeSendingData):
            app.fireCustomEvent(myCustomEventId)
            stopFlag.set() 


def run(context):

    global ui, app
    global myCustomEvent
    global stopFlag   
    global myThread

    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface

        # Register the custom event and connect the handler.
        myCustomEvent = app.registerCustomEvent(myCustomEventId)
        onThreadEvent = ThreadEventHandler()
        myCustomEvent.add(onThreadEvent)
        handlers.append(onThreadEvent)

        # Create a new thread for the other processing.       
        stopFlag = threading.Event()
        myThread = MyThread(stopFlag)

        qatRToolbar = ui.toolbars.itemById('QATRight')

        showPaletteCmdDef = ui.commandDefinitions.addButtonDefinition(thisAddinName + 'cmdef', thisAddinTitle, '', './resources')

        onCommandCreated = ShowPaletteCommandCreatedHandler()
        showPaletteCmdDef.commandCreated.add(onCommandCreated)
        handlers.append(onCommandCreated)

        qatRToolbar.controls.addCommand(showPaletteCmdDef, 'HealthStatusCommand', False)

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()), thisAddinName, 0, 0)

def stop(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface

        if handlers.count:
            myCustomEvent.remove(handlers[0])

        stopFlag.set() 

        app.unregisterCustomEvent(myCustomEventId)

        palette = ui.palettes.itemById(thisAddinName + 'Palette')
        if palette:
            palette.deleteMe()

        cmdDef = ui.commandDefinitions.itemById(thisAddinName + 'cmdef')
        if cmdDef:
            cmdDef.deleteMe()

        qatRToolbar = ui.toolbars.itemById('QATRight')
        cmd = qatRToolbar.controls.itemById(thisAddinName + 'cmdef')
        if cmd:
            cmd.deleteMe()

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()), thisAddinName, 0, 0)
