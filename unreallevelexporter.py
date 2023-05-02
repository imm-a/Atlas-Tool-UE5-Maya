import unreal
import sys, os, json, shutil
import subprocess

def export_textures(textures,meshName,meshIndex):
	filepath ='C:\\Users\\aimmaneni\\Documents\\T_'+str(meshIndex)+'_'+meshName
	
	index = 1
	for texture in textures:

		options = unreal.ImageWriteOptions()
		filename = filepath+str(index)+'.png'

		
		exportTask = unreal.AssetExportTask()
		exportTask.automated = True
		exportTask.filename = filepath+'_'+texture.get_name()+'_'+str(index)+'.png'
		exportTask.object = texture


		textureExporter = unreal.TextureExporterPNG()
		exportTask.exporter = textureExporter
		result = textureExporter.run_asset_export_task(exportTask)
		
		print(f' {result}')
		index += 1



def export_selected_fbx(file_path='C:\\Users\\aimmaneni\\Documents\\mappy.fbx'):
	selectedAssets = unreal.EditorLevelLibrary.get_selected_level_actors()
	index = 0
	asset_list = []
	for selectedAsset in selectedAssets:
		meshName = selectedAsset.get_actor_label() 
		textures = get_textures(selectedAsset.static_mesh_component.get_materials())
		asset_list.append(meshName)
		export_textures(textures,meshName,index)
		index += 1
	world = unreal.EditorLevelLibrary.get_editor_world()
	task = unreal.AssetExportTask()
	task.set_editor_property('selected', True)
	task.set_editor_property('filename', file_path)
	task.set_editor_property('automated', True)
	task.set_editor_property('object', world)

	fbx_options = unreal.FbxExportOption()
	fbx_options.set_editor_property('collision', False)
	fbx_options.set_editor_property('force_front_x_axis', False)
	fbx_options.set_editor_property('level_of_detail', False)
	task.set_editor_property('options', fbx_options)

	levelExporter = unreal.LevelExporterFBX()
	task.exporter = levelExporter
	result = levelExporter.run_asset_export_task(task)
	print ('Export Result: {}'.format(result))
	return asset_list

def get_textures(materials):
	textures = []	
	for material in materials:
		texParams = material.texture_parameter_values
		for texParam in texParams:
			texture = texParam.parameter_value
			textures.append(texture)
	return textures

def maya_process(asset_list):
	index = 0
	mayaprocs = []
	mayaPyPath = 'C:\\Program Files\\Autodesk\\Maya2023\\bin\\mayapy.exe'
	# path to the script you want to run inside Maya - r'" necessary if path has spaces, i.e. \Unreal Projects\
	scriptPath = './mayaatlas.py'
	folderName = "C:/Users/aimmaneni/Documents/"
	fbxFilePaths = "mappy.fbx"
	texFilePaths1 = ''
	texFilePaths2 = ''
	texFilePaths3 = ''
	files = os.listdir(folderName)
	textureFiles = []
	for f in files:
		for asset in asset_list:
			if f[4:].startswith(asset):
				if f[len(f)-5] == '1':
					if texFilePaths1 == '':
						texFilePaths1 += f
					else:
						texFilePaths1 += ','+f
				elif f[len(f)-5] == '2':
					if texFilePaths2 == '':
						texFilePaths2 += f
					else:
						texFilePaths2 += ','+f
				elif f[len(f)-5] == '3':
					if texFilePaths3 == '':
						texFilePaths3 += f
					else:
						texFilePaths3 += ','+f
				break
	print(texFilePaths1)
	print(texFilePaths2)
	print(texFilePaths3)
	if texFilePaths3 == '':
		texFilePaths3 = 'none'
	maya = subprocess.Popen(mayaPyPath + ' ' + scriptPath + ' ' + fbxFilePaths+' '+texFilePaths1+' '+texFilePaths2+' '+texFilePaths3+' '+folderName, stdout=subprocess.PIPE,stderr=subprocess.PIPE, encoding="utf-8")
	out,err = maya.communicate()
	exitcode = maya.returncode
	print(out)
	if str(exitcode) != '0':
		print(err)
		print(out)
	

asset_list = export_selected_fbx()

print(asset_list)
maya_process(asset_list)
#need to think about multiple material elements

#import meshes and textures. Duplicate the material instance of the og asset and assign new textures. then replace said asset.