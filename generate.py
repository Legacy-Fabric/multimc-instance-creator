#!/usr/bin/env python3
import os
import zipfile

loader: str = "0.14.24"
legacy_fixes: str = "legacy-fixes-1.0.1.jar"
lwjgl3: str = "3.1.6"
lwjgl2: str = "2.9.4-nightly-20150209"
lwjgl2_patch: str = "2.9.4+legacyfabric.5"


def mkdir_if_not_exists(path: str):
    if not os.path.exists(path):
        os.mkdir(path)


class Generator:
    def __init__(self, loader_version: str, minecraft_version: str, lwjgl_version: str, lwjgl_patch: str,
                 path: str = "temp"):
        self.lwjgl_version: str = lwjgl_version
        self.minecraft_version: str = minecraft_version
        self.loader_version: str = loader_version
        self.lwjgl_patch: str = lwjgl_patch
        self.path: str = path

    def process(self, subject: str) -> str:
        subject = subject.replace("${loader_version}", self.loader_version)
        subject = subject.replace("${minecraft_version}", self.minecraft_version)
        subject = subject.replace("${lwjgl_version}", self.lwjgl_version)
        subject = subject.replace("${lwjgl_patch}", self.lwjgl_patch)
        subject = subject.replace("${lwjgl_name}",
                                  "LWJGL 3" if self.lwjgl_version.startswith(
                                      "3") else "LWJGL 2")
        subject = subject.replace("${lwjgl_uid}",
                                  "org.lwjgl3" if self.lwjgl_version.startswith(
                                      "3") else "org.lwjgl")
        return subject

    def prepare_skeleton(self):
        mkdir_if_not_exists("temp")

        with open("skel/mmc-pack.json", "r") as f:
            with open("temp/mmc-pack.json", "w") as t:
                t.write(self.process(f.read()))

        with open("skel/instance.cfg", "r") as f:
            with open("temp/instance.cfg", "w") as t:
                t.write(self.process(f.read()))

        mkdir_if_not_exists("temp/patches")

        if not self.lwjgl_version.startswith("3"):
            with open("skel/patches/org.lwjgl.lwjgl.json", "r") as f:
                with open("temp/patches/org.lwjgl.lwjgl.json", "w") as t:
                    t.write(self.process(f.read()))

        intermediary_patch: str
        match self.minecraft_version:
            case "1.6.4":
                intermediary_patch = "skel/patches/net.fabricmc.intermediary.pre-1.7.json"
            case "1.5.2" | "1.4.7" | "1.3.2":
                intermediary_patch = "skel/patches/net.fabricmc.intermediary.pre-1.6.json"
            case _:
                intermediary_patch = "skel/patches/net.fabricmc.intermediary.json"

        with open(intermediary_patch, "r") as f:
            with open("temp/patches/net.fabricmc.intermediary.json", "w") as t:
                t.write(self.process(f.read()))

        with open("skel/legacyfabric.png", "rb") as f:
            with open("temp/legacyfabric.png", "wb") as t:
                t.write(f.read())

        if self.minecraft_version in ("1.8.9", "1.7.10", "1.6.4", "1.5.2", "1.4.7", "1.3.2"):
            mkdir_if_not_exists("temp/.minecraft")
            mkdir_if_not_exists("temp/.minecraft/mods")
            with open(f"skel/.minecraft/mods/{legacy_fixes}", "rb") as f:
                with open(f"temp/.minecraft/mods/{legacy_fixes}", "wb") as t:
                    t.write(f.read())

    def create_zip(self):
        with zipfile.ZipFile(f"out/legacyfabric-{self.minecraft_version}+loader.{self.loader_version}.zip", "w") as z:
            z.write("temp/mmc-pack.json", "mmc-pack.json")
            z.write("temp/instance.cfg", "instance.cfg")
            z.write("temp/patches/net.fabricmc.intermediary.json",
                    "patches/net.fabricmc.intermediary.json")
            z.write("temp/legacyfabric.png", "legacyfabric.png")

            if not self.lwjgl_version.startswith("3"):
                z.write("temp/patches/org.lwjgl.lwjgl.json",
                        "patches/org.lwjgl.json")

            if self.minecraft_version in ("1.8.9", "1.7.10", "1.6.4", "1.5.2", "1.4.7", "1.3.2"):
                z.write(f"temp/.minecraft/mods/{legacy_fixes}", f".minecraft/mods/{legacy_fixes}")

        self.cleanup()

    def cleanup(self):
        for root, dirs, files in os.walk(self.path, topdown=False):
            for file in files:
                os.remove(os.path.join(root, file))
            for dir in dirs:
                os.rmdir(os.path.join(root, dir))

        os.rmdir(self.path)


versions = [
    ("1.13.2", 3),
    ("1.12.2", 2),
    ("1.11.2", 2),
    ("1.10.2", 2),
    ("1.9.4", 2),
    ("1.8.9", 2),
    ("1.7.10", 2),
    ("1.6.4", 2),
    ("1.5.2", 2),
    ("1.4.7", 2),
    ("1.3.2", 2),
]

print(f"target loader: {loader}")
mkdir_if_not_exists("out")
for version, lwjgl in versions:
    lwjgl_version = lwjgl3 if lwjgl == 3 else lwjgl2
    lwjgl_patch = lwjgl3 if lwjgl == 3 else lwjgl2_patch
    print(f"generating {version} with LWJGL {lwjgl_patch}...")
    g = Generator(loader, version, lwjgl_version, lwjgl_patch)
    g.prepare_skeleton()
    g.create_zip()
