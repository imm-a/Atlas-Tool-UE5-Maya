# scriptPath var in the unreal code above points to this file.
import sys
import os
import maya.standalone as standalone
standalone.initialize(name='python')
import maya.cmds as cmds
import maya.mel as mel
import re 

# get fbx file path arg passed in via subprocess - sys.argv[n] returns nth arg included in subprocess Popen call.
fbxFilePath = sys.argv[1]

#print(sys.argv[2].split(','))
#print(fbxFilePathList)
#texFilePaths = ['C:/Users/aimmaneni/OneDrive - University of Central Florida/Amritha Immaneni/RPP/R4/T_frame_BaseColor.png','C:/Users/aimmaneni/OneDrive - University of Central Florida/Amritha Immaneni/RPP/R4/SM_Sock_T_Sock_BaseColor.png','C:/Users/aimmaneni/OneDrive - University of Central Florida/Amritha Immaneni/RPP/R4/T_Mask_BaseColor.png','C:/Users/aimmaneni/OneDrive - University of Central Florida/Amritha Immaneni/RPP/R4/T_LavaLamp_BaseColor.png']
texFilePaths = sys.argv[2].split(',')
print(f'texfilepath {texFilePaths}')
texFilePaths1 = sys.argv[3].split(',')
if sys.argv[4]!='none':
    texFilePaths2 = sys.argv[4].split(',')
folderName = sys.argv[5]
#texFilePaths1 = ['C:/Users/aimmaneni/OneDrive - University of Central Florida/Amritha Immaneni/RPP/R4/T_frame_Normal.png','C:/Users/aimmaneni/OneDrive - University of Central Florida/Amritha Immaneni/RPP/R4/SM_Sock_T_Sock_Normal.png','C:/Users/aimmaneni/OneDrive - University of Central Florida/Amritha Immaneni/RPP/R4/T_Mask_Normal.png','C:/Users/aimmaneni/OneDrive - University of Central Florida/Amritha Immaneni/RPP/R4/T_LavaLamp_Normal.png.png']
#texFilePaths2 = ['C:/Users/aimmaneni/OneDrive - University of Central Florida/Amritha Immaneni/RPP/R4/T_frame_OcclusionRoughnessMetallic.png','C:/Users/aimmaneni/OneDrive - University of Central Florida/Amritha Immaneni/RPP/R4/SM_Sock_T_Sock_OcclusionRoughnessMetallic.png','C:/Users/aimmaneni/OneDrive - University of Central Florida/Amritha Immaneni/RPP/R4/T_Mask_OcclusionRoughnessMetallic.png','C:/Users/aimmaneni/OneDrive - University of Central Florida/Amritha Immaneni/RPP/R4/T_LavaLamp_OcclusionRoughnessMetallic.png']


def listDifference(li1,li2):
    temp3 = []
    for element in li1:
        if element not in li2:
            temp3.append(element)
    return temp3

# no plugins are loaded by default in maya standalone - load fbx plugin
cmds.loadPlugin("fbxmaya.mll")

# sample maya function to import fbx
def importFBX(fbxFilePathList):
    index = 0

    if os.path.isfile(folderName+fbxFilePath):
        print ('importing ' + fbxFilePath)
        print(folderName+fbxFilePath)
        cmds.file(folderName+fbxFilePath, i = True)
        transform_objects = cmds.ls(tr = True)
        items = []
        for to in transform_objects:
            if to == 'front' or to == 'side' or to == 'persp' or to == 'top':
                continue
            items.append(to)
        print(items)
        index = 0
        for item in items:
            material,sg = create_material(f'Mat{index}')

            texture = texFilePaths[index]
            for tex in texFilePaths:
                if tex.find(item)!=1: #mapping mesh to texture
                    texture = tex
                    print('found the right texture')
                    break
            assign_texture_to_material(f'Tex{index}',material,folderName+texture)
            assign_material_to_mesh(item,material,sg)
            placeTexture(f'Tex{index}')
            print('Created tex')
            index += 1

        combine_meshes()
        layout_uvs()
        transfer_textures(folderName+"T_atlas_basecolor")

        index = 0
        for meshes in items:
            #Normal maps
            texture = texFilePaths1[index]
            for tex in texFilePaths1:
                if tex.find(meshes)!=1: #mapping mesh to texture
                    texture = tex
                    print('found the right texture')
                    break
            assign_other_textures(f'Tex{index}',folderName+texture) #assign the next set of textures to existing materials
            index += 1
        transfer_textures_other(folderName+"T_atlas_normal") #transfer the normal map textures

        if sys.argv[4]!='none':
            index = 0
            for meshes in items:
                #ARM
                texture = texFilePaths2[index]
                for tex in texFilePaths2:
                    if tex.find(meshes)!=1: #mapping mesh to texture
                        texture = tex
                        print('found the right texture')
                        break
                assign_other_textures(f'Tex{index}',folderName+texture) #assign the next set of textures to existing materials
                index += 1
            transfer_textures_other(folderName+"T_atlas_arm") #transfer the ARM map textures

        export_atlas_mesh(folderName+"atlashMesh.fbx")
            
            
        # print all geometry in the scene
                    
    else:
        print ('no file at: ' + fbxFilePath)
        

    

def create_material(matName):
    material = cmds.shadingNode("phong", asShader=True, name=matName)
    sg = cmds.sets(name="%s" % matName, empty=True, renderable=True, noSurfaceShader=True)
    cmds.connectAttr("%s.outColor" % material, "%s.surfaceShader" % sg)
    return material, sg

def assign_texture_to_material(texName,matName,imagePath):  
    cmds.shadingNode("file", asTexture=True, name=texName)
    cmds.connectAttr(f'{texName}.outColor', f'{matName}.color')
    #imagePath = 'C:/Users/aimmaneni/OneDrive - University of Central Florida/Amritha Immaneni/RPP/R4/T_frame_BaseColor.png'
    cmds.setAttr(f'{texName}.fileTextureName', imagePath, type="string")

def assign_material_to_mesh(mesh,matName,sg):
    cmds.select(mesh,r = True)
    cmds.sets(mesh, forceElement=sg)
    #cmds.hyperShade(assign=matName)

def placeTexture(texName):
    cmds.shadingNode('place2dTexture', asUtility=True, name="uvFileImage")
    cmds.defaultNavigation(connectToExisting=True, source='uvFileImage', destination=texName)

def combine_meshes():
    cmds.select(all = True)
    cmds.polyUnite(cmds.ls(selection = True), n = 'sourceMesh')
    cmds.delete(ch=True)

def layout_uvs():
    mainUVSet = cmds.polyUVSet(auv = True,query = True)[0]
    cmds.polyUVSet( copy=True, uvSet=mainUVSet )
    cmds.polyUVSet( rn=True, uvSet='uvSet1', newUVSet = 'atlas')
    cmds.polyMultiLayoutUV(uvs = 'atlas',lm = 1, sc = 1, rbf = 0, ps = 0.05, l = 2, gu = 1, gv = 1, psc = 0, su = 1, sv = 1, ou =0, ov = 0)

def transfer_textures(filename):
    cmds.duplicate('sourceMesh')
    cmds.rename('sourceMesh1','atlasMesh')
    cmds.surfaceSampler(target = 'atlasMeshShape', uvSet = 'atlas', targetUVSpace = 'atlas', source = 'sourceMeshShape', sourceUVSpace = 'atlas', mapOutput = 'diffuseRGB', mapWidth = 2048, mapHeight = 2048, max = 1, mapSpace = 'tangent', mapMaterials =1, shadows = 1, filename = filename, fileFormat = 'jpg', superSampling = 1, filterType = 0, filterSize = 3, overscan = 1, searchMethod = 0, useGeometryNormals = 1, ignoreMirroredFaces = 0, flipU = 0, flipV = 0 )

def assign_other_textures(texName,imagePath):
    cmds.setAttr(f'{texName}.fileTextureName', imagePath, type="string")

def transfer_textures_other(filename):
    cmds.surfaceSampler(target = 'atlasMeshShape', uvSet = 'atlas', targetUVSpace = 'atlas', source = 'sourceMeshShape', sourceUVSpace = 'atlas', mapOutput = 'diffuseRGB', mapWidth = 2048, mapHeight = 2048, max = 1, mapSpace = 'tangent', mapMaterials =1, shadows = 1, filename = filename, fileFormat = 'jpg', superSampling = 1, filterType = 0, filterSize = 3, overscan = 1, searchMethod = 0, useGeometryNormals = 1, ignoreMirroredFaces = 0, flipU = 0, flipV = 0 )

def export_atlas_mesh(filename):

    print(f'exporting {filename}')

    obj_export = filename
    cmds.select(cmds.ls('atlasMeshShape'))
    mainUVSet = cmds.polyUVSet(auv = True,query = True)[0]
    cmds.polyUVSet( reorder=True, nuv='atlas', uvSet=mainUVSet)
    cmds.polyUVSet( delete=True, uvSet=mainUVSet)
    mel.eval('FBXExportConstraints -v true')
    mel.eval('FBXExportTangents -v true')
    mel.eval('FBXExportCameras -v false')
    mel.eval('FBXExportSmoothMesh -v 0')
    mel.eval('FBXExportAnimationOnly -v false')
    mel.eval('FBXExport -f "{}" -s'.format(obj_export))


importFBX(fbxFilePath)