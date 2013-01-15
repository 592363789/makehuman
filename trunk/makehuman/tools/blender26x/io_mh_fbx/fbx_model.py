# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
import sys
from . import fbx
from .fbx_basic import *
from .fbx_props import *

#------------------------------------------------------------------
#   Connection node
#------------------------------------------------------------------

Prefix = {
    "Model" : "Model", 
    "Geometry" : "Geometry", 
    "Material" : "Material", 
    "Texture" : "Texture", 
    "Video" : "Video", 
    "AnimationStack" : "AnimStack", 
    "AnimationLayer" : "AnimLayer", 
    "AnimationCurveNode" : "AnimCurveNode", 
    "AnimationCurve" : "AnimCurve", 
    "NodeAttribute" : "NodeAttribute", 
    "Pose" : "Pose", 
    "Deformer" : {"Skin" : "Deformer", "Cluster" : "SubDeformer"},

    "Null" : None
}
    
class CConnection(CFbx):

    def __init__(self, type, subtype, btype):
        CFbx.__init__(self, type)
        self.subtype = subtype
        self.prefix = Prefix[type]
        self.btype = btype
        self.links = []
        self.children = []
        self.active = False
        self.isObjectData = False
        self.properties = None
        self.struct = {}
        print("__init__", self)

    def __repr__(self):
        return ("<CNode %d %s %s %s %s %s %s>" % (self.id, self.ftype, self.subtype, self.name, self.isModel, self.active, self.btype))
        
    def parse(self, pnode):     
        print(self, pnode)
        self.parseNodes(pnode.values[3:])
        return self

    def parseNodes(self, pnodes): 
        for pnode in pnodes:
            if pnode.key == 'Properties70':
                self.properties = CProperties70().parse(pnode)
                print("Props", self)
            elif len(pnode.values) == 1:
                self.struct[pnode.key] = pnode.values[0]
            elif len(pnode.values) > 1:
                self.struct[pnode.key] = pnode.values
            try:
                print("  ", pnode.key, self.struct[pnode.key])
            except:
                pass
        return self    


    def make(self, datum):
        CFbx.make(self)
        try:
            self.name = datum.name
        except AttributeError:
            pass
        return self
        
                
    def makeLink(self, parent):
        if self == parent:
            print("Linking to self", self)
            return
            halt
        self.links.append(parent)
        parent.children.append(self)
        
    def getParent(self, btype):
        nodes = []
        for node in self.links:
            if node.btype == btype:
                return node
        halt                
        
    def getChildren(self, btype):
        nodes = []
        for node in self.children:
            if node.btype == btype:
                nodes.append(node)
        return nodes                                
        
    def getProp(self, prop, default):
        return self.properties.getProp(prop, default)

    def writeHeader(self, fp):
        fp.write('    %s: %d, "%s::%s", "%s" {\n' % (self.ftype, self.id, self.prefix, self.name, self.subtype))

        
    def writeProps(self, fp):
        self.writeHeader(fp)
        if self.properties:
            self.properties.writeProps(fp)
        for key,value in self.struct.items():
            if isinstance(value, str):
                fp.write('        %s: "%s"\n' % (key,value))
            elif isinstance(value, list) or isinstance(value, tuple):
                fp.write('        %s' % key)
                c = ' '
                for x in value:
                    fp.write('%s %s' % (c,x))
                    c = ','
                fp.write('\n')
            else:
                fp.write('        %s: %s\n' % (key,value))
        fp.write('    }\n')


    def writeLinks(self, fp):
        if self.links:
            links = self.links
        else:
            links = [fbx.root]
        for node in links:
            self.writeLink(fp, node)
            

    def writeLink(self, fp, node, oo="OO", extra=""):
        fp.write(
            '    ;%s::%s, %s::%s\n' % (self.prefix, self.name, node.prefix, node.name) +
            '    C: "%s",%d,%d%s\n\n' % (oo, self.id, node.id, extra) )

#------------------------------------------------------------------
#   Root node
#------------------------------------------------------------------

class RootNode(CConnection):

    def __init__(self):
        CConnection.__init__(self, "Model", "", None)
        self.name = "RootNode"
        self.id = 0
        fbx.idstruct[0] = self
        self.active = True
        
    def writeProps(self, fp):
        return

    def writeLinks(self, fp):
        return

#------------------------------------------------------------------
#   Node Attribute node
#------------------------------------------------------------------

class CNodeAttribute(CConnection):
    propertyTemplate = (
"""    
        PropertyTemplate: "FbxCamera" {
            Properties70:  {
                P: "Color", "ColorRGB", "Color", "",0.8,0.8,0.8
                P: "Position", "Vector", "", "A",0,0,-50
                P: "UpVector", "Vector", "", "A",0,1,0
                P: "InterestPosition", "Vector", "", "A",0,0,0
                P: "Roll", "Roll", "", "A",0
                P: "OpticalCenterX", "OpticalCenterX", "", "A",0
                P: "OpticalCenterY", "OpticalCenterY", "", "A",0
                P: "BackgroundColor", "Color", "", "A",0.63,0.63,0.63
                P: "TurnTable", "Number", "", "A",0
                P: "DisplayTurnTableIcon", "bool", "", "",0
                P: "UseMotionBlur", "bool", "", "",0
                P: "UseRealTimeMotionBlur", "bool", "", "",1
                P: "Motion Blur Intensity", "Number", "", "A",1
                P: "AspectRatioMode", "enum", "", "",0
                P: "AspectWidth", "double", "Number", "",320
                P: "AspectHeight", "double", "Number", "",200
                P: "PixelAspectRatio", "double", "Number", "",1
                P: "FilmOffsetX", "Number", "", "A",0
                P: "FilmOffsetY", "Number", "", "A",0
                P: "FilmWidth", "double", "Number", "",0.816
                P: "FilmHeight", "double", "Number", "",0.612
                P: "FilmAspectRatio", "double", "Number", "",1.33333333333333
                P: "FilmSqueezeRatio", "double", "Number", "",1
                P: "FilmFormatIndex", "enum", "", "",0
                P: "PreScale", "Number", "", "A",1
                P: "FilmTranslateX", "Number", "", "A",0
                P: "FilmTranslateY", "Number", "", "A",0
                P: "FilmRollPivotX", "Number", "", "A",0
                P: "FilmRollPivotY", "Number", "", "A",0
                P: "FilmRollValue", "Number", "", "A",0
                P: "FilmRollOrder", "enum", "", "",0
                P: "ApertureMode", "enum", "", "",2
                P: "GateFit", "enum", "", "",0
                P: "FieldOfView", "FieldOfView", "", "A",25.1149997711182
                P: "FieldOfViewX", "FieldOfViewX", "", "A",40
                P: "FieldOfViewY", "FieldOfViewY", "", "A",40
                P: "FocalLength", "Number", "", "A",34.8932762167263
                P: "CameraFormat", "enum", "", "",0
                P: "UseFrameColor", "bool", "", "",0
                P: "FrameColor", "ColorRGB", "Color", "",0.3,0.3,0.3
                P: "ShowName", "bool", "", "",1
                P: "ShowInfoOnMoving", "bool", "", "",1
                P: "ShowGrid", "bool", "", "",1
                P: "ShowOpticalCenter", "bool", "", "",0
                P: "ShowAzimut", "bool", "", "",1
                P: "ShowTimeCode", "bool", "", "",0
                P: "ShowAudio", "bool", "", "",0
                P: "AudioColor", "Vector3D", "Vector", "",0,1,0
                P: "NearPlane", "double", "Number", "",10
                P: "FarPlane", "double", "Number", "",4000
                P: "AutoComputeClipPanes", "bool", "", "",0
                P: "ViewCameraToLookAt", "bool", "", "",1
                P: "ViewFrustumNearFarPlane", "bool", "", "",0
                P: "ViewFrustumBackPlaneMode", "enum", "", "",2
                P: "BackPlaneDistance", "Number", "", "A",4000
                P: "BackPlaneDistanceMode", "enum", "", "",1
                P: "ViewFrustumFrontPlaneMode", "enum", "", "",2
                P: "FrontPlaneDistance", "Number", "", "A",10
                P: "FrontPlaneDistanceMode", "enum", "", "",1
                P: "LockMode", "bool", "", "",0
                P: "LockInterestNavigation", "bool", "", "",0
                P: "BackPlateFitImage", "bool", "", "",0
                P: "BackPlateCrop", "bool", "", "",0
                P: "BackPlateCenter", "bool", "", "",1
                P: "BackPlateKeepRatio", "bool", "", "",1
                P: "BackgroundAlphaTreshold", "double", "Number", "",0.5
                P: "ShowBackplate", "bool", "", "",1
                P: "BackPlaneOffsetX", "Number", "", "A",0
                P: "BackPlaneOffsetY", "Number", "", "A",0
                P: "BackPlaneRotation", "Number", "", "A",0
                P: "BackPlaneScaleX", "Number", "", "A",1
                P: "BackPlaneScaleY", "Number", "", "A",1
                P: "Background Texture", "object", "", ""
                P: "FrontPlateFitImage", "bool", "", "",1
                P: "FrontPlateCrop", "bool", "", "",0
                P: "FrontPlateCenter", "bool", "", "",1
                P: "FrontPlateKeepRatio", "bool", "", "",1
                P: "Foreground Opacity", "double", "Number", "",1
                P: "ShowFrontplate", "bool", "", "",1
                P: "FrontPlaneOffsetX", "Number", "", "A",0
                P: "FrontPlaneOffsetY", "Number", "", "A",0
                P: "FrontPlaneRotation", "Number", "", "A",0
                P: "FrontPlaneScaleX", "Number", "", "A",1
                P: "FrontPlaneScaleY", "Number", "", "A",1
                P: "Foreground Texture", "object", "", ""
                P: "DisplaySafeArea", "bool", "", "",0
                P: "DisplaySafeAreaOnRender", "bool", "", "",0
                P: "SafeAreaDisplayStyle", "enum", "", "",1
                P: "SafeAreaAspectRatio", "double", "Number", "",1.33333333333333
                P: "Use2DMagnifierZoom", "bool", "", "",0
                P: "2D Magnifier Zoom", "Number", "", "A",100
                P: "2D Magnifier X", "Number", "", "A",50
                P: "2D Magnifier Y", "Number", "", "A",50
                P: "CameraProjectionType", "enum", "", "",0
                P: "OrthoZoom", "double", "Number", "",1
                P: "UseRealTimeDOFAndAA", "bool", "", "",0
                P: "UseDepthOfField", "bool", "", "",0
                P: "FocusSource", "enum", "", "",0
                P: "FocusAngle", "double", "Number", "",3.5
                P: "FocusDistance", "double", "Number", "",200
                P: "UseAntialiasing", "bool", "", "",0
                P: "AntialiasingIntensity", "double", "Number", "",0.77777
                P: "AntialiasingMethod", "enum", "", "",0
                P: "UseAccumulationBuffer", "bool", "", "",0
                P: "FrameSamplingCount", "int", "Integer", "",7
                P: "FrameSamplingType", "enum", "", "",1
            }
        }
""")

    def __init__(self, subtype, btype, typeflags):
        CConnection.__init__(self, 'NodeAttribute', subtype, btype)
        self.properties = None
        self.struct['TypeFlags'] = typeflags


    def parseNodes(self, pnodes):
        for pnode in pnodes:
            if pnode.key == 'Properties70':
                self.properties = CProperties70().parse(pnode)
            elif pnode.key == 'TypeFlags':
                self.typeflags = pnode.values[0]
        return self    


    def make(self, btype, props):
        CConnection.make(self, btype)
        if props:
            self.properties = CProperties70().make(props)
        if self.id == 0:
            halt
            
                    
            
#------------------------------------------------------------------
#   Model node
#------------------------------------------------------------------

class CModel(CConnection):
    propertyTemplate = (
"""
        PropertyTemplate: "FbxNode" {
            Properties70:  {
                P: "QuaternionInterpolate", "enum", "", "",0
                P: "RotationOffset", "Vector3D", "Vector", "",0,0,0
                P: "RotationPivot", "Vector3D", "Vector", "",0,0,0
                P: "ScalingOffset", "Vector3D", "Vector", "",0,0,0
                P: "ScalingPivot", "Vector3D", "Vector", "",0,0,0
                P: "TranslationActive", "bool", "", "",0
                P: "TranslationMin", "Vector3D", "Vector", "",0,0,0
                P: "TranslationMax", "Vector3D", "Vector", "",0,0,0
                P: "TranslationMinX", "bool", "", "",0
                P: "TranslationMinY", "bool", "", "",0
                P: "TranslationMinZ", "bool", "", "",0
                P: "TranslationMaxX", "bool", "", "",0
                P: "TranslationMaxY", "bool", "", "",0
                P: "TranslationMaxZ", "bool", "", "",0
                P: "RotationOrder", "enum", "", "",0
                P: "RotationSpaceForLimitOnly", "bool", "", "",0
                P: "RotationStiffnessX", "double", "Number", "",0
                P: "RotationStiffnessY", "double", "Number", "",0
                P: "RotationStiffnessZ", "double", "Number", "",0
                P: "AxisLen", "double", "Number", "",10
                P: "PreRotation", "Vector3D", "Vector", "",0,0,0
                P: "PostRotation", "Vector3D", "Vector", "",0,0,0
                P: "RotationActive", "bool", "", "",0
                P: "RotationMin", "Vector3D", "Vector", "",0,0,0
                P: "RotationMax", "Vector3D", "Vector", "",0,0,0
                P: "RotationMinX", "bool", "", "",0
                P: "RotationMinY", "bool", "", "",0
                P: "RotationMinZ", "bool", "", "",0
                P: "RotationMaxX", "bool", "", "",0
                P: "RotationMaxY", "bool", "", "",0
                P: "RotationMaxZ", "bool", "", "",0
                P: "InheritType", "enum", "", "",0
                P: "ScalingActive", "bool", "", "",0
                P: "ScalingMin", "Vector3D", "Vector", "",0,0,0
                P: "ScalingMax", "Vector3D", "Vector", "",1,1,1
                P: "ScalingMinX", "bool", "", "",0
                P: "ScalingMinY", "bool", "", "",0
                P: "ScalingMinZ", "bool", "", "",0
                P: "ScalingMaxX", "bool", "", "",0
                P: "ScalingMaxY", "bool", "", "",0
                P: "ScalingMaxZ", "bool", "", "",0
                P: "GeometricTranslation", "Vector3D", "Vector", "",0,0,0
                P: "GeometricRotation", "Vector3D", "Vector", "",0,0,0
                P: "GeometricScaling", "Vector3D", "Vector", "",1,1,1
                P: "MinDampRangeX", "double", "Number", "",0
                P: "MinDampRangeY", "double", "Number", "",0
                P: "MinDampRangeZ", "double", "Number", "",0
                P: "MaxDampRangeX", "double", "Number", "",0
                P: "MaxDampRangeY", "double", "Number", "",0
                P: "MaxDampRangeZ", "double", "Number", "",0
                P: "MinDampStrengthX", "double", "Number", "",0
                P: "MinDampStrengthY", "double", "Number", "",0
                P: "MinDampStrengthZ", "double", "Number", "",0
                P: "MaxDampStrengthX", "double", "Number", "",0
                P: "MaxDampStrengthY", "double", "Number", "",0
                P: "MaxDampStrengthZ", "double", "Number", "",0
                P: "PreferedAngleX", "double", "Number", "",0
                P: "PreferedAngleY", "double", "Number", "",0
                P: "PreferedAngleZ", "double", "Number", "",0
                P: "LookAtProperty", "object", "", ""
                P: "UpVectorProperty", "object", "", ""
                P: "Show", "bool", "", "",1
                P: "NegativePercentShapeSupport", "bool", "", "",1
                P: "DefaultAttributeIndex", "int", "Integer", "",-1
                P: "Freeze", "bool", "", "",0
                P: "LODBox", "bool", "", "",0
                P: "Lcl Translation", "Lcl Translation", "", "A",0,0,0
                P: "Lcl Rotation", "Lcl Rotation", "", "A",0,0,0
                P: "Lcl Scaling", "Lcl Scaling", "", "A",1,1,1
                P: "Visibility", "Visibility", "", "A",1
                P: "Visibility Inheritance", "Visibility Inheritance", "", "",1
            }
        }
""")

    def __init__(self, subtype, btype):
        CConnection.__init__(self, 'Model', subtype, btype)
        self.properties = None
        self.rna = None


    def parseNodes(self, pnodes):
        for pnode in pnodes:
            if pnode.key == 'Properties70':
                self.properties = CProperties70().parse(pnode)
        return self    


    def make(self, rna):
        CConnection.make(self, rna)
        self.rna = rna
        if rna.animation_data:
            act = rna.animation_data.action
            if act:
                alayer = fbx.nodes.alayers[act.name]
                CConnection.makeLink(alayer, self)
        

print("fbx_model imported")
