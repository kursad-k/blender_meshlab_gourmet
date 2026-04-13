import bpy
import os
import tempfile
import time
import hashlib
import subprocess


def debugPrint(*message):

    message_str = ', '.join(str(x) for x in message)
    os.system("echo %s" % message_str)
    print(message_str)
    return


def toggleTerminal():
    """Toggle the terminal only on Windows
    """
    if sys.platform.startswith('darwin'):
        pass

    elif os.name == 'nt':
        os.startfile(wm.mlm_script_path)

    elif os.name == 'posix':
        pass

    return {'FINISHED'}


class Scene:

    def __init__(self):

        self.Name = os.path.splitext(bpy.path.basename(bpy.data.filepath))[0]
        self.Path = bpy.data.filepath
        self.Dirname = os.path.dirname(self.Path)
        self.Objects = bpy.context.selected_objects
        self.Object = bpy.context.active_object
        self.ScriptsPath = bpy.utils.script_path_user()
        self.AppVersion = bpy.app.version
        self.ApiVersion = str(self.AppVersion[0]) + str(self.AppVersion[1])

    def setActiveObject(self, objname):
        """Sets the active object """

        if self.ApiVersion == "279":
            bpy.context.scene.objects.active = bpy.data.objects[objname]

        self.Object = bpy.context.active_object

    def selectObjectbyName(self, objname):
        """Select an object by name
        """
        bpy.ops.object.select_all(action='DESELECT')
        print(">> all objects are deselected")

        bpy.ops.object.select_pattern(pattern="{}".format(objname))
        print(">> {} is selected".format(objname))

        self.Object = bpy.context.selected_objects[0]
        print(">> {} is active object".format(str(self.Object)))

    def deselecObjects(self):
        for obj in bpy.context.selected_objects:
            if self.ApiVersion == "279":
                obj.select = False

            if self.ApiVersion == "289":
                obj.select_set(False)

        self.Objects = None

    def deactivateObject(self):
        if self.ApiVersion == "279":
            bpy.context.scene.objects.active = None

        if self.ApiVersion == "280":
            bpy.context.view_layer.objects.active = None

        self.Object = None

    def setSelectedAsActive(self):

        print("<< SELECTED OBJECT @ {} >>".format(
            bpy.context.selected_objects))
        print("<< ACTIVE OBJECT   @ {} >>".format(bpy.context.active_object))

        cur_selection = bpy.context.selected_objects[0]

        bpy.context.scene.objects.active = bpy.data.objects[cur_selection.name]
        self.Object = bpy.context.active_object

        print("<< SELECTED OBJECT @@ {} >>".format(
            bpy.context.selected_objects))
        print("<< ACTIVE OBJECT   @@ {} >>".format(bpy.context.active_object))

        return True


class Object:

    def __init__(self, id=None):

        if id is None:
            if not not bpy.context.selected_objects:
                self.Id = bpy.context.active_object
        else:
            self.Id = id
        self.Id = bpy.context.active_object

        self.Name = self.Id.name
        self.Color = self.Id.color
        self.Location = self.Id.location

        self.LocationW = self.Id.matrix_world.to_translation()
        self.RotationW = self.Id.matrix_world.to_euler('XYZ')
        self.ScaleW = self.Id.matrix_world.to_scale()

        self.Parent = self.Id.parent
        self.Bbox = self.Id.bound_box.data.scale
        self.Mode = self.Id.mode

    def isEditMode(self):
        """Check to see we are in edit  mode
        """

        if self.Id.mode == "EDIT":
            return True

        else:
            return False

    def objectMode(self):

        if self.isEditMode():
            bpy.ops.object.mode_set(mode="OBJECT")

        else:
            return True

        return

    def move(self, vec=(0, 0, 0)):
        self.Location += Vector(vec)
        return

    def convertTris2Quads(self):
        if not self.isEditMode():
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.tris_convert_to_quads()
            bpy.ops.object.editmode_toggle()

        if self.isEditMode():
            bpy.ops.mesh.tris_convert_to_quads()

    def transferObjectData(self, other):
        """self.Id to other.Id"""


class Io:
    """
    All the import/export utilities
    """

    def __init__(self):

        self.File_in = ""
        self.File_out = ""
        self.Format_in = ""
        self.Format_out = "obj"
        self.Parameters = ""

        self.Tempfolder = tempfile.gettempdir()

        self.Exportname = bpy.context.active_object.name
        self.Exportfile = self.Exportname + "." + self.Format_out
        self.Exportfullpath = os.path.join(self.Tempfolder, self.Exportfile)

        self.Tempname = hashlib.sha256(str(
            time.time()).encode('utf-8')).hexdigest()[1:12]
        self.Tempexportfile = os.path.join(
            self.Tempfolder, self.Tempname + "." + self.Format_out)
        self.ScriptsDir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "scripts")
        wm = bpy.context.window_manager
        meshlab_folder = getattr(wm, "mlg_meshlab_folder", "")
        self.MeshlabServerExe = os.path.join(meshlab_folder, "meshlabserver.exe")

    def obj_Export(self, file=None):
        """bpy.ops.export_scene.obj()
        bpy.ops.export_scene.obj(filepath="", check_existing=True,
        filter_glob="*.obj;*.mtl", use_selection=False,
        use_animation=False, use_mesh_modifiers=True,
        use_mesh_modifiers_render=False, use_edges=True,
        use_smooth_groups=False, use_smooth_groups_bitflags=False,
        use_normals=True, use_uvs=True, use_materials=True,
        use_triangles=False, use_nurbs=False, use_vertex_groups=False,
        use_blen_objects=True, group_by_object=False, group_by_material=False,
        keep_vertex_order=False, global_scale=1, path_mode='AUTO', axis_forward='-Z', axis_up='Y')
        """

        if file:
            print("exporting ->> %s" % file)

            bpy.ops.export_scene.obj(filepath=file,
                                     use_selection=True,
                                     use_materials=False,
                                     keep_vertex_order=True,
                                     use_edges=False,
                                     use_smooth_groups=True,
                                     use_vertex_groups=False,
                                     use_triangles=True)

        else:

            print("exporting ->> %s" % self.Tempexportfile)

            bpy.ops.export_scene.obj(filepath=self.Tempexportfile,
                                     use_selection=True,
                                     use_materials=False,
                                     keep_vertex_order=True,
                                     use_edges=False,
                                     use_smooth_groups=False,
                                     use_vertex_groups=False)

    def obj_Import(self, file=None):
        """bpy.ops.import_scene.obj(filepath="", filter_glob="*.obj;*.mtl",
        use_edges=True, use_smooth_groups=True, use_split_objects=True,
        use_split_groups=True, use_groups_as_vgroups=False,
        use_image_search=True, split_mode='ON', global_clight_size=0,
        axis_forward='-Z', axis_up='Y')
        """

        try:
            if file == None:
                bpy.ops.import_scene.obj(filepath=self.Tempexportfile,
                                         axis_forward='Z')
                print(
                    "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
                )
                print(
                    "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
                )
                print(
                    "%%%%%%%%%%%%%%%%%%%%%%%%%%%IMPORTING THE OBJECT NOW%%%%%%%%%%%%%%%%%%%%%%%"
                )
                print(
                    "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
                )
                print(
                    "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
                )
                print(
                    "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
                )
            else:
                bpy.ops.import_scene.obj(filepath=file)
                print(
                    "##########################################################################"
                )
                print(
                    "##########################################################################"
                )
                print(
                    "###########################IMPORTING THE OBJECT NOW#######################"
                )
                print(
                    "##########################################################################"
                )
                print(
                    "##########################################################################"
                )
                print(
                    "##########################################################################"
                )

            return True

        except Exception as error:
            print('.OBJ import failed >> ' + repr(error))
            return False

    def obj_CleanUp(self, file=None):

        if file:
            os.remove(file)
            return True
        else:
            os.remove(self.Tempexportfile)
            return False

    def import_fbx():
        return

    def export_fbx():
        return

    def import_alembic():
        return

    def export_alembic():
        return

    def meshlab_Convert(self):
        """meshlabserver -i input.obj -o output.ply -m vc fq wt -s meshclean.mlx
        """

        print("running meshlabserver")
        subprocess.run(
            '"%s" -i "%s" -o "%s" -s "%s" '
            % (self.MeshlabServerExe, self.Tempexportfile,
               os.path.join(self.Tempfolder, self.Tempname + ".ply"),
               os.path.join(self.ScriptsDir, "filter.mlx")),
            shell=True)
        return

    def meshlab_Process(self):
        """meshlabserver -i input.obj -o output.ply -m vc fq wt -s meshclean.mlx
        """

        print("running meshlabserver")
        subprocess.run(
            '"%s" -i "%s" -o "%s" -l x -s "%s" '
            %
            (self.MeshlabServerExe, self.Tempexportfile,
             os.path.join(self.Tempfolder, self.Tempname + "_processed.obj"),
             os.path.join(self.ScriptsDir, "RemeshPoissonScreen.mlx")),
            shell=True)
        return os.path.join(self.Tempfolder, self.Tempname + "_processed.obj")

    def getTempFileName():
        tempfolder = tempfile.gettempdir()

        return
