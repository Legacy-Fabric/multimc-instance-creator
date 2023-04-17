import os
import zipfile

loader: str = "0.14.19"
lwjgl3: str = "3.1.6"
lwjgl2: str = "2.9.4-nightly-20150209"


def mkdir_if_not_exists(path: str):
    if not os.path.exists(path):
        os.mkdir(path)


class Generator:
    def __init__(self, loader_version: str, minecraft_version: str, lwjgl_version: str, path: str = "temp"):
        self.lwjgl_version: str = lwjgl_version
        self.minecraft_version: str = minecraft_version
        self.loader_version: str = loader_version
        self.path: str = path

    def process(self, subject: str) -> str:
        subject = subject.replace("${loader_version}", self.loader_version)
        subject = subject.replace("${minecraft_version}", self.minecraft_version)
        subject = subject.replace("${lwjgl_version}", self.lwjgl_version)
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
        if self.minecraft_version == "1.6.4" or "1.5.2" or "1.4.7" or "1.3.2":
            with open("skel/patches/net.fabricmc.intermediary.pre-1.7.json", "r") as f:
                with open("temp/patches/net.fabricmc.intermediary.json", "w") as t:
                    t.write(self.process(f.read()))
        else:
            with open("skel/patches/net.fabricmc.intermediary.json", "r") as f:
                with open("temp/patches/net.fabricmc.intermediary.json", "w") as t:
                    t.write(self.process(f.read()))

        with open("skel/legacyfabric.png", "rb") as f:
            with open("temp/legacyfabric.png", "wb") as t:
                t.write(f.read())

    def create_zip(self):
        with zipfile.ZipFile(f"out/legacyfabric-{self.minecraft_version}+loader.{self.loader_version}.zip", "w") as z:
            z.write("temp/mmc-pack.json", "mmc-pack.json")
            z.write("temp/instance.cfg", "instance.cfg")
            z.write("temp/patches/net.fabricmc.intermediary.json",
                    "patches/net.fabricmc.intermediary.json")
            z.write("temp/legacyfabric.png", "legacyfabric.png")

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
    print(f"generating {version} with LWJGL {lwjgl_version}...")
    g = Generator(loader, version, lwjgl_version)
    g.prepare_skeleton()
    g.create_zip()

# g = Generator(loader, "1.13.2", lwjgl3)
# g.prepare_skeleton()
# g.create_zip()
