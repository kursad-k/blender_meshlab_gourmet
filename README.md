# MeshLab Gourmet

![Screenshot](assets/meshlabgourmet_screen.png)


_See the bottom of the document for the release notes._



## Brief

This add-on streamlines editing and processing meshes in external applications such as MeshLab. It currently supports MeshLab only and aims to make export, processing, and re-import seamless.


## Features

* Run custom MeshLab scripts on the currently selected object.

* Add new MeshLab scripts to the script library while Blender is running.

* Open the selected object in MeshLab and import the edited mesh back into Blender.

* Edit the currently selected script in a text editor.

* Works with vertex-only meshes as long as the selected MeshLab script supports them.

* Includes a sample MeshLab script library.

* Supports Linux, Windows, and macOS.

## Planned

* Support OpenFlipper as an additional mesh processing backend.

* Support batch processing of multiple mesh objects.

* Support frame by frame processing. All the processed frames will be saved as individual mesh files.

* Selectable exchange formats such as `.fbx` or Collada. The add-on currently uses `.obj`.

* Better mesh processing progress display.

* Ability to replace the original mesh.

* Add a dedicated script parameter panel for the selected script.

* Clone scripts.

* Copy mesh, modifier, and animation data from the original object.

## Installation

### Requirements

* Blender 2.79
* MeshLab 2018

Older versions of MeshLab might work, but the add-on is only tested with MeshLab 2018.

**Option 1**: Extract the downloaded zip file to your Blender user `addons` folder. Then restart Blender or press `F8` to refresh add-ons.

**Option 2**: Open Blender preferences, go to `Add-ons`, and use `Install addon from file` to install the zip.

After installation, enable the add-on from the `Add-ons` tab. Search for `meshlabman`, enable it, and set the required preference such as `Meshlab 2018 folder`. Then save your preferences.

You can find the add-on in the Object properties panel for the selected object. This placement may change in future releases.

## FAQ

* **Does it work with 2.8?**

Yes. Blender 2.80 support was added in v1.2.



* **Can I process point/vertex cloud in Meshlab via this addon?**

Yes, as long as you use the right MeshLab scripts. For operations like remeshing, make sure the point cloud includes vertex normals.



* **Does it work with multiple selections?**

Yes, but the processed result is re-imported as a single mesh. Batch processing for multiple selections is planned.



* **Do you plan to support other mesh processing applications?**

Yes. More mesh processing backends may be added in the future.



* **How can I create Meshlab scripts?**

Open MeshLab, import your model, and apply the filters in the order you want. Then go to `Filters -> Show current filter script`, review the listed operations, and save the script. Save it to the add-on's default `scripts` folder under Blender's user add-on directory, or to your custom script folder if you configured one.

Two things to watch for: avoid using `Preview` while building the filter stack, because MeshLab may not record those filters, and make sure the saved script uses the `.mlx` extension.



* **I applied script X and I am getting some crazy results. Is the addon broken?**

Usually not. The script likely needs adjustment for your mesh size or topology. You can edit the script from the add-on panel or save a revised one from MeshLab.



* **My meshes are always triangulated. Can the addon import them as quads?**

Not directly. MeshLab processes triangulated polygon data, so there is limited control here. You can try `tris to quad` after import in Edit Mode.




* **Can I surface/remesh my particle animation data?**
Yes. You can instance the particle cloud to a single vertex, then process that mesh with the add-on. At the moment only the active frame is processed. Animated mesh processing is planned for v2.




* **Where can I download MeshLab 2018?**

The most recent releases can be found here, although they generally publish macOS releases there first: https://github.com/cnr-isti-vclab/meshlab/releases

You can download Windows builds here: https://ci.appveyor.com/project/cignoni/meshlab/build/artifacts


## Release Notes for v1.1

* Option to keep the processed meshes in the temp folder
* Automatic conversion of imported meshes to quads from triangles
* The addon now detects no edits in Meshlab, no unnecessary imports anymore
* The exported mesh is triangulated prior to processing for better compatibility with MeshLab/MeshLabServer
* Object rotation is maintained across the versions
* Better handling of the imported mesh's pivot

## Release Notes for v1.2

* Blender 2.80 update
* Some scripts are updated


## Release Notes for v1.2.1

- Hot fix for 2.80
