#!/usr/bin/python
# -*- coding: utf-8 -*-

""" 
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Thomas Larsson

**Copyright(c):**      MakeHuman Team 2001-2011

**Licensing:**         GPL3 (see also http://sites.google.com/site/makehumandocs/licensing)

**Coding Standards:**  See http://sites.google.com/site/makehumandocs/developers-guide

Abstract
--------
MakeHuman to Collada (MakeHuman eXchange format) exporter. Collada files can be loaded into
Blender by collada_import.py.

TO DO

"""

import os
import numpy as np
import gui3d
import module3d
import mh
import aljabr
import gui
import filechooser as fc
import log

#import cProfile

import armature
from armature import transformations as tm
import warpmodifier
import humanmodifier
import posemode

#
#   Pose library
#

"""
class PoseModifier(humanmodifier.GenderAgeMuscleWeightModifier):
    def __init__(self, template):        
        humanmodifier.GenderAgeMuscleWeightModifier.__init__(self, template)
        self.isPose = True

"""        
class PoseModifier(warpmodifier.WarpModifier):
    def __init__(self, template):
        warpmodifier.WarpModifier.__init__(self, template, "body", "GenderAgeMuscleWeightModifier") 
        self.isPose = True


class PoseLoadTaskView(gui3d.TaskView):

    def __init__(self, category):

        self.systemPoses = os.path.join('data', 'poses')
        self.userPoses = os.path.join(mh.getPath(''), 'data', 'poses')

        self.dirty = False
        
        gui3d.TaskView.__init__(self, category, 'Poses')
        if not os.path.exists(self.userPoses):
            os.makedirs(self.userPoses)
        self.filechooser = self.addTopWidget(fc.FileChooser([self.systemPoses, self.userPoses], 'mhp', 'png', 'data/clothes/notfound.png'))
        self.addLeftWidget(self.filechooser.sortBox)
        self.update = self.filechooser.sortBox.addWidget(gui.Button('Check for updates'))
        self.mediaSync = None

        @self.filechooser.mhEvent
        def onFileSelected(filepath):

            self.loadMhpFile(filepath)
            mh.changeCategory('Modelling')
            
        @self.update.mhEvent
        def onClicked(event):
            self.syncMedia()
 

    def loadMhpFile(self, filepath): 
    
        log.message("Load Mhp: %s", filepath)

        human = gui3d.app.selectedHuman

        if os.path.basename(filepath) == "clear.mhp":
            posemode.exitPoseMode()
            posemode.resetPoseMode()
            return

        posemode.enterPoseMode()
        folder = os.path.dirname(filepath)
        (fname, ext) = os.path.splitext(os.path.basename(filepath))
        modpath = '%s/${gender}-${age}-${tone}-${weight}-%s.target' % (folder, fname)
        modpath = modpath.replace("\\","/")
        log.debug('PoseLoadTaskView.loadMhpFile: %s %s', filepath, modpath)
        modifier = PoseModifier(modpath)
        modifier.updateValue(human, 1.0)
        
        amt = human.armature
        if amt:
            pass
            #amt.rebuild()
        else:
            amt = human.armature = armature.rigdefs.createRig(human, "soft1")            
        amt.setModifier(modifier)
        amt.readMhpFile(filepath)
        #amt.listPose()

 
    def onShow(self, event):

        # When the task gets shown, set the focus to the file chooser
        gui3d.TaskView.onShow(self, event)
        gui3d.app.selectedHuman.hide()
        self.filechooser.setFocus()


    def onHide(self, event):
        gui3d.app.selectedHuman.show()
        gui3d.TaskView.onHide(self, event)
                

    def onHumanChanging(self, event):
        posemode.changePoseMode(event)

                
    def onHumanChanged(self, event):
        posemode.changePoseMode(event)


    def loadHandler(self, human, values):
        pass
        
    def saveHandler(self, human, file):
        pass

# This method is called when the plugin is loaded into makehuman
# The app reference is passed so that a plugin can attach a new category, task, or other GUI elements


def load(app):
    category = app.getCategory('Library')
    taskview = category.addTask(PoseLoadTaskView(category))

    app.addLoadHandler('poses', taskview.loadHandler)
    app.addSaveHandler(taskview.saveHandler)

# This method is called when the plugin is unloaded from makehuman
# At the moment this is not used, but in the future it will remove the added GUI elements


def unload(app):
    pass
