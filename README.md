## io_import_milo

A plugin for Blender to import milo files from **Rock Band** and **Guitar Hero** games, with texture loading support.

---

### Features
- Loads any `.milo` extension  
- Imports models and renders them in Blender
- Supports texture loading  

---

### Limitations
- Does not load Wii character animations
- Does not support bone parenting
- Milo exporting is beta and issues may arise

---

### How to Use
- Install the plugin in Blender
- Navigate to File -> Import -> Harmonix Milo Engine, then click the one that opens what you wanna import
- In the file system, go to the folder that contains the file you wanna import
- Once you find it, import it!
- You should now see it loaded in the Blender scene

---

### How to Import Character Animations (VERY BETA):
## NOTE: Weights aren't 100% on X360 or PS3 (except older games), for TBRB and on it's best to use Wii models + X360 / PS3 anims

### Milo:
- Import character
- Import the milo containing the animation you want
- When imported, click on the armature, open the sidebar, and find the Animation Panel
- On the animation panel, find the one you want to load then click it
- The animation is now loaded! To view it with meshes, just put a modifier on each one for the object "Armature"
### ACP (More beta than milo):
- Import character
- Select the armature
- Import the .acp containing the animation you want
- The animation is now loaded! To view it with meshes, just put a modifier on each one for the object "Armature"