# -*- coding: utf-8 -*-
"""
Created on Wed Mar 23 10:51:54 2022

 
@author: AMIN
"""

################################################################################################################

import os
import shutil
import traceback
from pathlib import Path

import pypyodbc

# server location and get_cursor
conn = pypyodbc.get_cursor(
    "DRIVER={SQL Server};SERVER=E-U10HMXIFWS16\SQLEXPRESS;DATABASE=HMXIFdb;Trusted_Connection=yes"
)
c = conn.cursor()

# different locations to be used later
input_dir = Path("G:\\ctdata\\_FOR ARCHIVING")
input_dir1 = Path("Z:\PERM_STORAGE")
input_dir2 = Path("Z:\\SAT_STORAGE")


# Organise folder structure, extract metadata_panel and export to SQL
def start():
    for scan_dir in (d for d in input_dir.glob("*_*") if d.is_dir()):
        folder_maker(scan_dir)

        # Find _CTUSERFORM.txt and copy to 'reconstructed data'
        for txt in scan_dir.glob("*.txt"):
            if txt.name == "_CTUSERFORM.txt":
                try:
                    archive(scan_dir)
                    print(scan_dir.name)
                    # Path
                    path_src = os.path.join(scan_dir, txt.name)
                    path_dest = os.path.join(scan_dir, "reconstructed data")
                    print(path_src)
                    print(path_dest)
                    path = shutil.copy(path_src, path_dest)
                # print(path)

                except Exception:
                    print("Error processing [{0}]".format(txt))
                    traceback.print_exc()
            else:
                try:
                    print("uu")
                except Exception:
                    print("Error processing [{0}]".format(txt))
                    traceback.print_exc()

        # Find projections and MOVE to "PERMANENT STORAGE" folder
        for tif in scan_dir.glob("*.tif"):
            if tif.is_file():
                try:
                    if txt.name == "_CTUSERFORM.txt":
                        f = txt.open()
                        lines = f.readlines()
                        Project_ID = str(lines[0])[13:]
                        Project_ID = Project_ID.strip()
                        print(Project_ID)
                    path_dest = os.path.join(input_dir1, Project_ID, scan_dir.name)

                    print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
                    print(tif)
                    # open method used to open different extension image file

                    check_server2(Project_ID, scan_dir)
                    shutil.copy(tif, path_dest)
                    # select a single project to archive in database

                    # delete the projection
                    os.remove(tif)

                except Exception:
                    print("Error processing [{0}]".format(tif))
                    traceback.print_exc()
            else:
                print("No Projections!")

        # Find xml files and MOVE to PERMANENT STORAGE and COPY to 'reconstructed data' (--> SAT storage)
        for xml in scan_dir.glob("*.xml"):
            if xml.is_file():
                try:
                    # Path
                    path_src = os.path.join(scan_dir, xml)
                    path_destR = os.path.join(scan_dir, "reconstructed data")

                    path = shutil.copy(path_src, path_destR)

                    shutil.copy(xml, path_dest)
                    os.remove(xml)
                except Exception:
                    print("Error processing [{0}]".format(xml))
                    traceback.print_exc()
            else:
                print("No XML!")

        # Find xtekct files and MOVE to PERMANENT STORAGE and COPY to 'reconstructed data' (--> SAT storage)
        for xtekct in scan_dir.glob("*.xtekct"):

            try:
                # Path

                path_src = os.path.join(scan_dir, xtekct)
                path_destR = os.path.join(scan_dir, "reconstructed data")
                path = shutil.copy(path_src, path_destR)

                # obtain metada and update database
                process_xtekct(xtekct)
                # shutil.copy(xtekct,path_dest)
                os.remove(xtekct)
            except Exception:
                print("Error processing [{0}]".format(xtekct))
                traceback.print_exc()

        # Find ANG files and MOVE to PERMANENT STORAGE and COPY to 'reconstructed data' (--> SAT storage)
        for ANG in scan_dir.glob("*.ANG"):
            if ANG.is_file():
                try:
                    # Path
                    path_src = os.path.join(scan_dir, ANG)
                    path_destR = os.path.join(scan_dir, "reconstructed data")

                    path = shutil.copy(path_src, path_destR)

                    shutil.copy(ANG, path_dest)
                    os.remove(ANG)
                except Exception:
                    print("Error processing [{0}]".format(ANG))
                    traceback.print_exc()
            else:
                print("No ANG!")

        path_dest2 = os.path.join(input_dir2, Project_ID)

        # Find reconstruction(s) and MOVE to 'reconstructed data' folder
        for recon_dir in (d for d in scan_dir.glob("*_01") if d.is_dir()):
            move_dir(recon_dir, "reconstructed data")
        for recon_dir in (d for d in scan_dir.glob("*recon") if d.is_dir()):
            move_dir(recon_dir, "reconstructed data")

        ##############
        for recon_dir in (d for d in scan_dir.glob("*_processing") if d.is_dir()):
            path_dest3 = os.path.join(path_dest2, "_processing")
            shutil.copytree(recon_dir, path_dest3)

        for recon_dir in (d for d in scan_dir.glob("*_tmp") if d.is_dir()):
            path_dest4 = os.path.join(path_dest2, "_tmp")
            shutil.copytree(recon_dir, path_dest4)

        path_dest = os.path.join(input_dir2, Project_ID, scan_dir.name)
        for recon_dir in (
            d for d in scan_dir.glob("*reconstructed data") if d.is_dir()
        ):
            path_dest3 = os.path.join(path_dest, "reconstructed data")

            shutil.copytree(recon_dir, path_dest3)

        ########################

        # Find CentreSlice(s) folder  and MOVE to PERMANENT STORAGE
        for centreslice_dir in (d for d in scan_dir.glob("*CentreSlice") if d.is_dir()):
            path_dest2 = os.path.join(path_dest, "CentreSlice")
            shutil.copytree(centreslice_dir, path_dest2)


#           shutil.rmtree(str(scan_dir))

# Make Project_ID get_cursor folder with subfolders as follow "reconstructed data", "processing", "tmp" sub-folders


def folder_maker(scan_dir):
    os.makedirs(str(scan_dir) + "\\_processing", exist_ok=True)
    os.makedirs(str(scan_dir) + "\\_tmp", exist_ok=True)
    os.makedirs(str(scan_dir) + "\\reconstructed data", exist_ok=True)


def move_dir(file, dir):
    if dir == "VOL":
        Target_dir = Path.joinpath(file.parents[1], dir, file.name)
    else:
        Target_dir = Path.joinpath(file.parents[0], dir, file.name)
    os.rename(str(file), str(Target_dir))


## Here we open the generated _CTUSERFORM containing administratives information. 9all the primary key in the database)
def archive(scan_dir):
    # Find Project ID from _CTUSERFORM
    for txt in scan_dir.glob("*.txt"):
        try:
            if txt.name == "_CTUSERFORM.txt":
                f = txt.open()
                lines = f.readlines()
                global Project_ID

                Project_ID = str(lines[0])[13:]
                Project_ID = Project_ID.strip()
                Instrument_ID = str(lines[1])[16:]
                User_ID = str(lines[2])[10:]

                global SCAN_ID
                SCAN_ID = str(lines[3])[10:]
                print(Project_ID)
                print(SCAN_ID)
                check_server(Project_ID)

            #  INSERT INTO TABLE_NAME (COLUMN_NAME) VALUES ("the values")`
            #  c.execute("INSERT INTO Project_info (Proj_ID) VALUES (Project_ID)")
            #   conn.commit()

        except Exception:
            print("Error processing [{0}]".format(txt))
            traceback.print_exc()


def process_xtekct(xtekct):
    try:

        myfile = open(xtekct, "r")
        data_dict = {}
        for line in myfile:
            if (
                line.startswith("DICOMTags")
                or line.startswith("[")
                or line.startswith("\n")
            ):
                continue
            k, v = line.strip().split("=")
            data_dict[k.strip()] = v.strip()

        myfile.close()

        voltage = data_dict["XraykV"]
        print(voltage)
        amperage = data_dict["XrayuA"]
        print(amperage)
        exposure = data_dict["XraykV"]
        print(exposure)
        projections = data_dict["Projections"]
        print(projections)
        voxel_size = data_dict["VoxelSizeX"]
        Filter_Material = data_dict["Filter_Material"]
        filter_thick = data_dict["Filter_ThicknessMM"]

        c.execute(
            "INSERT INTO XCT_settings (voltage,amperage,exposure,projections,voxel_size,Filter_Material ,filter_thick,SCAN_ID, Proj_ID)VALUES ( ?,?,?,?,?,?,?,?,?) ",
            (
                voltage,
                amperage,
                exposure,
                projections,
                voxel_size,
                Filter_Material,
                filter_thick,
                SCAN_ID,
                Project_ID,
            ),
        )
        # c.execute("UPDATE  XCT_settings  SET voltage=?,amperage=?,exposure=?,projections=?,voxel_size=?,Filter_Material=?,filter_thick=?,SCAN_ID=? WHERE Proj_ID=?", (voltage,amperage,exposure,projections,voxel_size,Filter_Material,filter_thick,SCAN_ID,Project_ID))

        print("Record inserted successfully into Laptop table")

    except c.Error as error:
        print("Failed to insert into MySQL table {}".format(error))

    #  finally:
    #     if connection.is_connected():
    ##        cursor.close()
    #      connection.close()
    #     print("MySQL connection is closed")

    print("iggggggggggggggggi")
    print("iggggggggggggggggi")


def get_size(path):
    total_size = 0
    for root, dirs, files in os.walk(path):
        for f in files:
            fp = os.path.join(root, f)
            total_size += os.path.getsize(fp)
    return total_size


# check if the project folder exist in all storage servers


def check_server(Project_ID):
    ProjFolder1 = Path.joinpath(input_dir1, Project_ID)
    ProjFolder2 = Path.joinpath(input_dir2, Project_ID)
    if ProjFolder1.is_dir() and ProjFolder2.is_dir():
        print("Y")
    else:
        os.makedirs(str(input_dir1) + "\\" + Project_ID, exist_ok=True)
        os.makedirs(str(input_dir2) + "\\" + Project_ID, exist_ok=True)


def check_server2(Project_ID, scan_dir):
    scanFolder1 = Path.joinpath(input_dir1, scan_dir.name)
    scanFolder2 = Path.joinpath(input_dir2, scan_dir.name)
    if scanFolder1.is_dir():
        print("Y")
    else:
        os.makedirs(
            str(input_dir1) + "\\" + Project_ID + "\\" + scan_dir.name, exist_ok=True
        )

    if scanFolder2.is_dir():
        print("Y")
    else:

        os.makedirs(
            str(input_dir2) + "\\" + Project_ID + "\\" + scan_dir.name, exist_ok=True
        )


# Run the script
print(start())
conn.commit()
# conn.close()
