# -*- coding: utf-8 -*-
"""
Created on Fri Mar  4 13:30:56 2016

@author: aming
"""


import math
import os
import random
import re
import shutil
import time

# import pypyodbc
import traceback
from pathlib import Path
from tkinter import *
from tkinter import filedialog, font
from xml.dom import minidom


def sequence(*functions):
    def func(*args, **kwargs):
        return_value = None
        for function in functions:
            return_value = function(*args, **kwargs)
        return return_value

    return func


class Demo1:
    def __init__(self, win):

        self.win = win
        win.geometry("950x600")
        win.title("THE CT USER FORM")
        win.configure(bg="purple")

        self.frame0 = Frame(self.win, borderwidth=5, relief=GROOVE)

        Label(self.frame0, text="Date (dd/mm/yyyy)").grid(row=5, column=0, sticky=W)
        self.date = StringVar()
        self.date.set(time.strftime("%Y-%m-%d"))
        self.date = Entry(
            self.frame0,
            textvariable=self.date,
        )

        self.date.grid(row=6, column=0, sticky=W)

        Label(self.frame0, text="IAC Project Identifier").grid(
            row=5, column=2, sticky=W
        )
        self.pr_code = Entry(
            self.frame0,
        )
        self.pr_code.grid(row=6, column=2, sticky=E)
        self.frame0.pack(side=TOP, fill=X, padx=5, pady=5)

        Label(self.frame0, text="           ").grid(row=5, column=3, sticky=S + E)

        Label(self.frame0, text="Instruments                        ").grid(
            row=5, column=4, sticky=E
        )
        self.listbox4 = Listbox(self.frame0, width=20, height=2, exportselection=0)
        self.listbox4.grid(row=6, column=4, sticky=W)
        scrollbar = Scrollbar(self.frame0, orient="vertical")
        scrollbar.config(command=self.listbox4.yview)
        scrollbar.grid(row=6, column=5, sticky=E)
        self.listbox4.config(yscrollcommand=scrollbar.set)
        self.listbox4.insert(END, "Versa 520")
        self.listbox4.insert(END, "Nikon")
        self.listbox4.insert(END, "NanoCT")
        self.listbox4.insert(END, "XXXX")
        self.listbox4.bind("<<ListboxSelect>>", self.onselect3)  # create the onselect2

        self.frame1 = Frame(self.win, borderwidth=5, relief=GROOVE)
        self.frame1.pack(side=TOP, fill=X, padx=5, pady=5)
        Label(self.frame1, text="Tomographer").grid(row=8, column=0, sticky=W)
        self.tom = Entry(
            self.frame1,
        )
        self.tom.grid(row=8, column=1, sticky=W)

        Label(self.frame1, text="Project type").grid(row=8, column=2, sticky=E)
        self.listbox0 = Listbox(self.frame1, width=20, height=2, exportselection=0)
        self.listbox0.grid(row=8, column=3, sticky=W)
        scrollbar = Scrollbar(self.frame1, orient="vertical")
        scrollbar.config(command=self.listbox0.yview)
        scrollbar.grid(row=8, column=4, sticky=W + N)
        self.listbox0.config(yscrollcommand=scrollbar.set)
        self.listbox0.insert(END, "NHM project")
        self.listbox0.insert(END, "Research project")
        self.listbox0.insert(END, "Commercial project")
        self.listbox0.insert(END, "Pilot project")
        self.listbox0.bind("<<ListboxSelect>>", self.onselect)

        self.frame2 = Frame(self.win, borderwidth=5, relief=GROOVE)
        self.frame2.pack(side=TOP, fill=X, padx=5, pady=5)
        Label(self.frame2, text="Name of your project").grid(row=11, column=0, sticky=E)
        self.project_name = Entry(self.frame2)
        self.project_name.grid(row=11, column=1)

        Button(
            self.frame2, text="Check if in database", command=self.valid_access
        ).grid(row=11, column=2, sticky=E)
        self.frame2.update()

        Label(self.frame2, text="Lead researcher name:").grid(
            row=11, column=3, sticky=W
        )
        self.lead_researcher = Entry(self.frame2)
        self.lead_researcher.grid(row=11, column=4)

        Label(self.frame2, text="Affiliation:").grid(row=11, column=5, sticky=E)
        self.listbox2 = Listbox(self.frame2, width=20, height=2, exportselection=0)
        self.listbox2.grid(row=11, column=6, sticky=E)
        scrollbar = Scrollbar(self.frame2, orient="vertical")
        scrollbar.config(command=self.listbox2.yview)
        scrollbar.grid(row=11, column=7, sticky=W)
        self.listbox2.config(yscrollcommand=scrollbar.set)
        self.listbox2.insert(END, "Natural History Museum")
        self.listbox2.insert(END, "Imperial College")
        self.listbox2.insert(END, "British Library")
        self.listbox2.insert(END, "Oxford University")
        self.listbox2.insert(END, "Kew Gardens")
        self.listbox2.insert(END, "  entry")
        self.listbox2.insert(END, "Other")
        self.listbox2.bind("<<ListboxSelect>>", self.onselect2)

        self.frame3 = Frame(self.win, borderwidth=5, relief=GROOVE)
        self.frame3.pack(side=TOP, fill=X, padx=5, pady=5)
        self.frame3b = Frame(self.win, borderwidth=5, relief=GROOVE)
        self.frame3b.pack(side=TOP, fill=X, padx=5, pady=5)

        self.frame4 = Frame(self.win, borderwidth=5, relief=GROOVE)
        self.frame4.pack(side=TOP, fill=X, padx=5, pady=5)
        Label(self.frame4, text="Comments:").grid(row=17, column=0, sticky=W)
        self.comments = Entry(self.frame4, width=50)
        self.comments.grid(row=17, column=1)

    def check_dataB(self):
        # self.a=random.randint(1,2)  #to delete
        existing_proj = c.execute(
            "SELECT Project_Name FROM Project_Info WHERE Project_Name=?",
            (self.proj_name,),
        )
        existing_proj = c.fetchone()
        existing_proj = str(existing_proj)
        existing_proj = existing_proj[2:-3]
        if self.proj_name.lower() == existing_proj.lower():  # self.a==2:
            top2 = Toplevel()
            top2.geometry("200x50")
            msg = Label(top2, text=" Project already exist ", font=self.shape)
            msg.pack(side=TOP)
            top2.after(1500, lambda: top2.destroy())

    def valid_access(self):
        conn = pypyodbc.connect(
            "DRIVER={SQL Server};SERVER=sqlhoratiolive\live;DATABASE=service_CT_Scan_live;Trusted_Connection=yes"
        )
        c = conn.cursor()
        self.proj_name = self.project_name.get()
        self.existing_proj = c.execute(
            "SELECT Project_Name FROM CT_Scan_Database WHERE Project_Name=?",
            (self.proj_name,),
        )
        self.existing_proj = c.fetchone()
        self.existing_proj = str(self.existing_proj)
        self.existing_proj = self.existing_proj[2:-3]
        if self.proj_name.lower() == self.existing_proj.lower():
            top2 = Toplevel()
            top2.geometry("200x50")
            msg = Label(top2, text=" Project already exist ", font=self.shape)
            msg.pack(side=TOP)
            top2.after(1500, lambda: top2.destroy())
        else:
            Label(self.frame2, text="What is the funding source?").grid(
                row=12, column=0, sticky=W
            )
            self.funding = Entry(self.frame2)
            self.funding.grid(row=12, column=1)

            Label(self.frame2, text="Is it a confidencial project?").grid(
                row=12, column=2, sticky=W
            )

            self.var1 = IntVar()
            Checkbutton(self.frame2, text="Yes   ", variable=self.var1).grid(
                row=12, column=3, sticky=W
            )

    def closure(self):
        self.items1 = self.listbox0.curselection()
        self.items2 = self.listbox2.curselection()

        if len(self.items1) == 0 or len(self.items2) == 0:
            top = Toplevel()
            top.title("About this application...")
            top.geometry("300x100")
            msg = Label(top, text="Please answer all questions", font=self.shape)
            msg.pack(side=TOP)
            button = Button(top, text="OK", command=top.destroy)
            button.pack(side=BOTTOM, fill=X, padx=5, pady=5)

    def onselect(self, event):
        w = event.widget
        index = int(w.curselection()[0])
        # value = w.get(index)
        # print ('You selected item %d: "%s"' % (index, value))
        if index == 0:

            Label(self.frame1, text="Curator name ").grid(row=11, column=0, sticky=E)
            self.curator = Entry(
                self.frame1,
            )
            self.curator.grid(row=11, column=1, sticky=E)

            Label(self.frame1, text="Collection name").grid(row=11, column=2, sticky=E)
            self.listbox3 = Listbox(self.frame1, width=20, height=2, exportselection=0)
            self.listbox3.grid(row=11, column=3, sticky=W)
            scrollbar = Scrollbar(self.frame1, orient="vertical")
            scrollbar.config(command=self.listbox3.yview)
            scrollbar.grid(row=11, column=4, sticky=W)
            self.listbox3.config(yscrollcommand=scrollbar.set)
            self.listbox3.insert(END, "Zoology")
            self.listbox3.insert(END, "Botany")
            self.listbox3.insert(END, "Mineralogy")
            self.listbox3.insert(END, "Paleontology")
            self.listbox3.insert(END, "Entomology")
            self.listbox3.insert(END, "Other")

            Label(self.frame1, text="Specimen name").grid(row=11, column=5, sticky=E)
            self.specimen = Entry(
                self.frame1,
            )
            self.specimen.grid(row=11, column=6, sticky=W)

            Label(self.frame1, text="NHM accession number").grid(
                row=11, column=7, sticky=W
            )
            self.accession = Entry(
                self.frame1,
            )
            self.accession.grid(row=11, column=8, sticky=W)
            self.frame1.update

        elif index != 2:

            Label(self.frame1, text="Sample type    ", bg="white", fg="red").grid(
                row=11, column=0, sticky=E
            )
            self.spltyp = Entry(
                self.frame1,
            )
            self.spltyp.grid(row=11, column=1, sticky=E)
            self.frame1.update

    def onselect2(self, event):
        wi = event.widget
        indexi = int(wi.curselection()[0])
        # value = w.get(index)
        # print ('You selected item %d: "%s"' % (index, value))
        if indexi == 6:
            Label(self.frame3, text="Specify affiliation").grid(
                row=16, column=6, sticky=E
            )
            self.sp_affil = Entry(
                self.frame3,
            )
            self.sp_affil.grid(row=16, column=7, sticky=E)
            self.frame3.update

    def onselect3(self, event):
        wii = event.widget
        indexii = int(wii.curselection()[0])
        # value = w.get(index)
        # print ('You selected item %d: "%s"' % (index, value))
        if indexii == 1:
            Label(self.frame3b, text="Metal target").grid(row=17, column=0, sticky=E)
            self.listbox1 = Listbox(self.frame3b, width=20, height=2, exportselection=0)
            self.listbox1.grid(row=17, column=1, sticky=W)
            scrollbar = Scrollbar(self.frame3b, orient="vertical")
            scrollbar.config(command=self.listbox1.yview)
            scrollbar.grid(row=17, column=2, sticky=W)
            self.listbox1.config(yscrollcommand=scrollbar.set)
            self.listbox1.insert(END, "Tungsten")
            self.listbox1.insert(END, "Copper")
            self.listbox1.insert(END, "Molybdenum")
            self.listbox1.insert(END, "4th entry")
            self.frame3b.update
            self.frame3.update
            self.shape = font.Font(
                size=10, weight="bold"
            )  # you don't have to use Helvetica or bold, this is just an example
            ###saving directoriES
            self.frame4 = Frame(self.win, borderwidth=5, relief=GROOVE, bg="white")
            self.frame4.pack(side=LEFT, fill=X, padx=5, pady=5)
            # button1
            Button(
                self.frame4,
                borderwidth=2,
                text="SAVE \nHounsfield C:\\ ",
                font=self.shape,
                fg="white",
                bg="red",
                command=sequence(self.closure, self.sav1),
            ).grid(row=18, column=0, sticky=E)
            # button2
            Button(
                self.frame4,
                borderwidth=2,
                text="SAVE \nHounsfield D:\\ ",
                font=self.shape,
                fg="white",
                bg="red",
                command=sequence(self.closure, self.sav2),
            ).grid(row=18, column=1, sticky=W)
            # button2
            Button(
                self.frame4,
                borderwidth=2,
                text="SAVE \n        Elliott C:\\         ",
                font=self.shape,
                fg="white",
                bg="black",
                command=sequence(self.closure, self.sav3),
            ).grid(row=18, column=2, sticky=W)
            # button2
            Button(
                self.frame4,
                borderwidth=2,
                text="SAVE \n        Elliott D:\\         ",
                font=self.shape,
                fg="white",
                bg="black",
                command=sequence(self.closure, self.sav4),
            ).grid(row=18, column=3, sticky=W)
            self.photo = PhotoImage(
                file="C:/Users/aming/Desktop/nhmlogo.png", width=350, height=122
            )
            Label(self.frame4, text="           ", bg="white").grid(
                row=18, column=5, sticky=S + E
            )
            Label(self.frame4, image=self.photo, bg="white").grid(
                row=18, column=6, sticky=E
            )
            self.frame4.update

        if indexii == 0:
            Label(self.frame3, text="Camera Binning").grid(row=17, column=0, sticky=W)
            self.bin = Entry(
                self.frame3,
            )
            self.bin.grid(row=18, column=0, sticky=W)

            Label(self.frame3, text="Source Filter").grid(row=19, column=5, sticky=E)
            self.listboxf = Listbox(self.frame3, width=20, height=2, exportselection=0)
            self.listboxf.grid(row=20, column=5, sticky=E)
            scrollbar = Scrollbar(self.frame3, orient="vertical")
            scrollbar.config(command=self.listboxf.yview)
            scrollbar.grid(row=20, column=6, sticky=W)
            self.listboxf.config(yscrollcommand=scrollbar.set)
            self.listboxf.insert(END, "LE1")
            self.listboxf.insert(END, "LE2")
            self.listboxf.insert(END, "LE3")
            self.listboxf.insert(END, "LE4")
            self.listboxf.insert(END, "LE5")
            self.listboxf.insert(END, "LE6")
            self.listboxf.insert(END, "x")
            self.listboxf.insert(END, "x")
            self.listboxf.insert(END, "x")
            self.listboxf.insert(END, "x")
            self.listboxf.insert(END, "x")
            self.listboxf.insert(END, "x")
            self.listboxf.insert(END, "x")
            self.listboxf.insert(END, "x")
            self.listboxf.insert(END, "x")
            Label(self.frame3, text="Voltage").grid(row=17, column=2, sticky=W)
            self.volt = Entry(
                self.frame3,
            )
            self.volt.grid(row=18, column=2, sticky=W)

            Label(self.frame3, text="Current").grid(row=17, column=3, sticky=W)
            self.amp = Entry(
                self.frame3,
            )
            self.amp.grid(row=18, column=3, sticky=W)

            Label(self.frame3, text="Source-RA distance").grid(
                row=17, column=4, sticky=W
            )
            self.src_dist = Entry(
                self.frame3,
            )
            self.src_dist.grid(row=18, column=4, sticky=W)

            Label(self.frame3, text="Detector-RA distance").grid(
                row=17, column=5, sticky=W
            )
            self.det_dist = Entry(
                self.frame3,
            )
            self.det_dist.grid(row=18, column=5, sticky=W)

            Label(self.frame3, text="Projections").grid(row=19, column=0, sticky=W)
            self.proj = Entry(
                self.frame3,
            )
            self.proj.grid(row=20, column=0, sticky=W)

            Label(self.frame3, text="Pixel size").grid(row=19, column=1, sticky=W)
            self.pix_siz = Entry(
                self.frame3,
            )
            self.pix_siz.grid(row=20, column=1, sticky=W)

            Label(self.frame3, text="Exposure Time").grid(row=19, column=2, sticky=W)
            self.exp = Entry(
                self.frame3,
            )
            self.exp.grid(row=20, column=2, sticky=W)

            Label(self.frame3, text="Optical Magnification").grid(
                row=19, column=3, sticky=E
            )
            self.listboxa = Listbox(self.frame3, width=20, height=2, exportselection=0)
            self.listboxa.grid(row=20, column=3, sticky=E)
            scrollbar = Scrollbar(self.frame3, orient="vertical")
            scrollbar.config(command=self.listboxa.yview)
            scrollbar.grid(row=20, column=4, sticky=W)
            self.listboxa.config(yscrollcommand=scrollbar.set)
            self.listboxa.insert(END, "0.4X")
            self.listboxa.insert(END, "4X")
            self.listboxa.insert(END, "20X")
            self.listboxa.insert(END, "40X")

            self.frame3.update
            self.frame3b.update
            self.shape = font.Font(
                size=10, weight="bold"
            )  # you don't have to use Helvetica or bold, this is just an example
            self.frame4 = Frame(self.win, borderwidth=5, relief=GROOVE, bg="white")
            self.frame4.pack(side=LEFT, fill=X, padx=5, pady=5)
            Button(
                self.frame4,
                borderwidth=2,
                text="SAVE \n VERSA 520 D:\\ ",
                font=self.shape,
                fg="white",
                bg="blue",
                command=sequence(self.closure, self.sav5),
            ).grid(row=18, column=0, sticky=W)
            self.photo = PhotoImage(
                file="C:/Users/aming/Desktop/nhmlogo.png", width=350, height=122
            )
            Label(self.frame4, text="           ", bg="white").grid(
                row=18, column=1, sticky=S + E
            )
            Label(self.frame4, image=self.photo, bg="white").grid(
                row=18, column=2, sticky=E
            )
            self.frame4.update

    ##############SAVING THE OUTPUTS

    def sav1(self):
        if len(self.items1) != 0 and len(self.items2) != 0:
            q = filedialog.asksaveasfilename(
                defaultextension=".txt",
                initialdir=" \\\\MIN-2835K4J\\C$\\CT Data\\",
                filetypes=[("text files", ".txt")],
                title="Pick a directory",
                initialfile="_CTUSERFORM.txt",
            )

            addinfo = open(q, "w")
            addinfo.write(" date: " + self.date.get())
            addinfo.write("\n IAC Project Identifier: " + self.pr_code.get())
            addinfo.write("\n Tomographer: " + self.tom.get())
            addinfo.write(
                "\n Equipment used: " + self.listbox4.get(self.listbox4.curselection())
            )
            addinfo.write("\n                  ")

            addinfo.write(
                "\n Project type: " + self.listbox0.get(self.listbox0.curselection())
            )
            if int(self.listbox0.curselection()[0]) == 0:
                addinfo.write("\n Curator name: " + self.curator.get())
                addinfo.write(
                    "\n Collection name: "
                    + self.listbox3.get(self.listbox3.curselection())
                )
                addinfo.write("\n Specimen name: " + self.specimen.get())
                addinfo.write("\n NHM accession number: " + self.accession.get())
            elif int(self.listbox0.curselection()[0]) != 0:
                addinfo.write("\n Curator name: " + "not relevant")
                addinfo.write("\n Collection name: " + "not relevant")
                addinfo.write("\n Sample type: " + self.spltyp.get())
                addinfo.write("\n NHM accession number: " + "not relevant")
            addinfo.write("\n                  ")

            addinfo.write("\n Name of your project: " + self.project_name.get())
            addinfo.write("\n Lead researcher: " + self.lead_researcher.get())
            if int(self.listbox2.curselection()[0]) != 6:
                addinfo.write(
                    "\n Affiliation: " + self.listbox2.get(self.listbox2.curselection())
                )
            elif int(self.listbox2.curselection()[0]) == 6:
                addinfo.write("\n Affiliation: " + self.sp_affil.get())
            if self.proj_name.lower() != self.existing_proj.lower():
                addinfo.write("\n Existing project: " + "No")
                addinfo.write("\n Funding source: " + self.funding.get())
                if self.var1.get() == 0:
                    addinfo.write("\n Confidentiality: " + "no")
                else:
                    addinfo.write("\n Confidentiality: " + "yes")
            elif self.proj_name.lower() == self.existing_proj.lower():
                addinfo.write("\n Existing project: " + "Yes")
            addinfo.write("\n                  ")

            if int(self.listbox2.curselection()[0]) == 1:
                addinfo.write(
                    "\n Metal target: "
                    + self.listbox1.get(self.listbox1.curselection())
                )
            elif int(self.listbox0.curselection()[0]) == 0:

                addinfo.write("\n Camera Binning: " + self.bin.get())
                addinfo.write(
                    "\n Source Filter" + self.listboxf.get(self.listboxf.curselection())
                )
                addinfo.write("\n Voltage: " + self.volt.get())
                addinfo.write("\n Current: " + self.amp.get())
                addinfo.write("\n Source-RA distance: " + self.src_dist.get())
                addinfo.write("\n Detector-RA distance: " + self.det_dist.get())
                addinfo.write("\n Projections: " + self.proj.get())
                addinfo.write("\n Pixel size: " + self.pix_siz.get())
                addinfo.write("\n Exposure Time: " + (self.exp.get()))
                addinfo.write(
                    "\n Optical Magnification: "
                    + self.listboxa.get(self.listboxa.curselection())
                )

                addinfo.write("\n Comments:" + self.comments.get())

            addinfo.close()
            return

    def sav2(self):
        if len(self.items1) != 0 and len(self.items2) != 0:
            q = filedialog.asksaveasfilename(
                defaultextension=".txt",
                initialdir=" \\MIN-2835K4J\\CT Data\\",
                filetypes=[("text files", ".txt")],
                title="Pick a directory",
                initialfile="_CTUSERFORM.txt",
            )

            addinfo = open(q, "w")
            addinfo.write(" date: " + self.date.get())
            addinfo.write("\n IAC Project Identifier: " + self.pr_code.get())
            addinfo.write("\n Tomographer: " + self.tom.get())
            addinfo.write(
                "\n Equipment used: " + self.listbox4.get(self.listbox4.curselection())
            )
            addinfo.write("\n                  ")

            addinfo.write(
                "\n Project type: " + self.listbox0.get(self.listbox0.curselection())
            )
            if int(self.listbox0.curselection()[0]) == 0:
                addinfo.write("\n Curator name: " + self.curator.get())
                addinfo.write(
                    "\n Collection name: "
                    + self.listbox3.get(self.listbox3.curselection())
                )
                addinfo.write("\n Specimen name: " + self.specimen.get())
                addinfo.write("\n NHM accession number: " + self.accession.get())
            elif int(self.listbox0.curselection()[0]) != 0:
                addinfo.write("\n Curator name: " + "not relevant")
                addinfo.write("\n Collection name: " + "not relevant")
                addinfo.write("\n Sample type: " + self.spltyp.get())
                addinfo.write("\n NHM accession number: " + "not relevant")
            addinfo.write("\n                  ")

            addinfo.write("\n Name of your project: " + self.project_name.get())
            addinfo.write("\n Lead researcher: " + self.lead_researcher.get())
            if int(self.listbox2.curselection()[0]) != 6:
                addinfo.write(
                    "\n Affiliation: " + self.listbox2.get(self.listbox2.curselection())
                )
            elif int(self.listbox2.curselection()[0]) == 6:
                addinfo.write("\n Affiliation: " + self.sp_affil.get())
            if self.proj_name.lower() != self.existing_proj.lower():
                addinfo.write("\n Existing project: " + "No")
                addinfo.write("\n Funding source: " + self.funding.get())
                if self.var1.get() == 0:
                    addinfo.write("\n Confidentiality: " + "no")
                else:
                    addinfo.write("\n Confidentiality: " + "yes")
            elif self.proj_name.lower() == self.existing_proj.lower():
                addinfo.write("\n Existing project: " + "Yes")
            addinfo.write("\n                  ")

            if int(self.listbox2.curselection()[0]) == 1:
                addinfo.write(
                    "\n Metal target: "
                    + self.listbox1.get(self.listbox1.curselection())
                )
            elif int(self.listbox0.curselection()[0]) == 0:

                addinfo.write("\n Camera Binning: " + self.bin.get())
                addinfo.write(
                    "\n Source Filter" + self.listboxf.get(self.listboxf.curselection())
                )
                addinfo.write("\n Voltage: " + self.volt.get())
                addinfo.write("\n Current: " + self.amp.get())
                addinfo.write("\n Source-RA distance: " + self.src_dist.get())
                addinfo.write("\n Detector-RA distance: " + self.det_dist.get())
                addinfo.write("\n Projections: " + self.proj.get())
                addinfo.write("\n Pixel size: " + self.pix_siz.get())
                addinfo.write("\n Exposure Time: " + (self.exp.get()))
                addinfo.write(
                    "\n Optical Magnification: "
                    + self.listboxa.get(self.listboxa.curselection())
                )

                addinfo.write("\n Comments:" + self.comments.get())

            addinfo.close()
            return

    def sav3(self):
        if len(self.items1) != 0 and len(self.items2) != 0:
            q = filedialog.asksaveasfilename(
                defaultextension=".txt",
                initialdir=" \\MIN-2835K4J\\CT Data\\",
                filetypes=[("text files", ".txt")],
                title="Pick a directory",
                initialfile="_CTUSERFORM.txt",
            )

            addinfo = open(q, "w")
            addinfo.write(" date: " + self.date.get())
            addinfo.write("\n IAC Project Identifier: " + self.pr_code.get())
            addinfo.write("\n Tomographer: " + self.tom.get())
            addinfo.write(
                "\n Equipment used: " + self.listbox4.get(self.listbox4.curselection())
            )
            addinfo.write("\n                  ")

            addinfo.write(
                "\n Project type: " + self.listbox0.get(self.listbox0.curselection())
            )
            if int(self.listbox0.curselection()[0]) == 0:
                addinfo.write("\n Curator name: " + self.curator.get())
                addinfo.write(
                    "\n Collection name: "
                    + self.listbox3.get(self.listbox3.curselection())
                )
                addinfo.write("\n Specimen name: " + self.specimen.get())
                addinfo.write("\n NHM accession number: " + self.accession.get())
            elif int(self.listbox0.curselection()[0]) != 0:
                addinfo.write("\n Curator name: " + "not relevant")
                addinfo.write("\n Collection name: " + "not relevant")
                addinfo.write("\n Sample type: " + self.spltyp.get())
                addinfo.write("\n NHM accession number: " + "not relevant")
            addinfo.write("\n                  ")

            addinfo.write("\n Name of your project: " + self.project_name.get())
            addinfo.write("\n Lead researcher: " + self.lead_researcher.get())
            if int(self.listbox2.curselection()[0]) != 6:
                addinfo.write(
                    "\n Affiliation: " + self.listbox2.get(self.listbox2.curselection())
                )
            elif int(self.listbox2.curselection()[0]) == 6:
                addinfo.write("\n Affiliation: " + self.sp_affil.get())
            if self.proj_name.lower() != self.existing_proj.lower():
                addinfo.write("\n Existing project: " + "No")
                addinfo.write("\n Funding source: " + self.funding.get())
                if self.var1.get() == 0:
                    addinfo.write("\n Confidentiality: " + "no")
                else:
                    addinfo.write("\n Confidentiality: " + "yes")
            elif self.proj_name.lower() == self.existing_proj.lower():
                addinfo.write("\n Existing project: " + "Yes")
            addinfo.write("\n                  ")

            if int(self.listbox2.curselection()[0]) == 1:
                addinfo.write(
                    "\n Metal target: "
                    + self.listbox1.get(self.listbox1.curselection())
                )
            elif int(self.listbox0.curselection()[0]) == 0:

                addinfo.write("\n Camera Binning: " + self.bin.get())
                addinfo.write(
                    "\n Source Filter" + self.listboxf.get(self.listboxf.curselection())
                )
                addinfo.write("\n Voltage: " + self.volt.get())
                addinfo.write("\n Current: " + self.amp.get())
                addinfo.write("\n Source-RA distance: " + self.src_dist.get())
                addinfo.write("\n Detector-RA distance: " + self.det_dist.get())
                addinfo.write("\n Projections: " + self.proj.get())
                addinfo.write("\n Pixel size: " + self.pix_siz.get())
                addinfo.write("\n Exposure Time: " + (self.exp.get()))
                addinfo.write(
                    "\n Optical Magnification: "
                    + self.listboxa.get(self.listboxa.curselection())
                )

                addinfo.write("\n Comments:" + self.comments.get())

            addinfo.close()
            return

    def sav4(self):
        if len(self.items1) != 0 and len(self.items2) != 0:
            q = filedialog.asksaveasfilename(
                defaultextension=".txt",
                initialdir=" \\MIN-2835K4J\\CT Data\\",
                filetypes=[("text files", ".txt")],
                title="Pick a directory",
                initialfile="_CTUSERFORM.txt",
            )

            addinfo = open(q, "w")
            addinfo.write(" date: " + self.date.get())
            addinfo.write("\n IAC Project Identifier: " + self.pr_code.get())
            addinfo.write("\n Tomographer: " + self.tom.get())
            addinfo.write(
                "\n Equipment used: " + self.listbox4.get(self.listbox4.curselection())
            )
            addinfo.write("\n                  ")

            addinfo.write(
                "\n Project type: " + self.listbox0.get(self.listbox0.curselection())
            )
            if int(self.listbox0.curselection()[0]) == 0:
                addinfo.write("\n Curator name: " + self.curator.get())
                addinfo.write(
                    "\n Collection name: "
                    + self.listbox3.get(self.listbox3.curselection())
                )
                addinfo.write("\n Specimen name: " + self.specimen.get())
                addinfo.write("\n NHM accession number: " + self.accession.get())
            elif int(self.listbox0.curselection()[0]) != 0:
                addinfo.write("\n Curator name: " + "not relevant")
                addinfo.write("\n Collection name: " + "not relevant")
                addinfo.write("\n Sample type: " + self.spltyp.get())
                addinfo.write("\n NHM accession number: " + "not relevant")
            addinfo.write("\n                  ")

            addinfo.write("\n Name of your project: " + self.project_name.get())
            addinfo.write("\n Lead researcher: " + self.lead_researcher.get())
            if int(self.listbox2.curselection()[0]) != 6:
                addinfo.write(
                    "\n Affiliation: " + self.listbox2.get(self.listbox2.curselection())
                )
            elif int(self.listbox2.curselection()[0]) == 6:
                addinfo.write("\n Affiliation: " + self.sp_affil.get())
            if self.proj_name.lower() != self.existing_proj.lower():
                addinfo.write("\n Existing project: " + "No")
                addinfo.write("\n Funding source: " + self.funding.get())
                if self.var1.get() == 0:
                    addinfo.write("\n Confidentiality: " + "no")
                else:
                    addinfo.write("\n Confidentiality: " + "yes")
            elif self.proj_name.lower() == self.existing_proj.lower():
                addinfo.write("\n Existing project: " + "Yes")
            addinfo.write("\n                  ")

            if int(self.listbox2.curselection()[0]) == 1:
                addinfo.write(
                    "\n Metal target: "
                    + self.listbox1.get(self.listbox1.curselection())
                )
            elif int(self.listbox0.curselection()[0]) == 0:

                addinfo.write("\n Camera Binning: " + self.bin.get())
                addinfo.write(
                    "\n Source Filter" + self.listboxf.get(self.listboxf.curselection())
                )
                addinfo.write("\n Voltage: " + self.volt.get())
                addinfo.write("\n Current: " + self.amp.get())
                addinfo.write("\n Source-RA distance: " + self.src_dist.get())
                addinfo.write("\n Detector-RA distance: " + self.det_dist.get())
                addinfo.write("\n Projections: " + self.proj.get())
                addinfo.write("\n Pixel size: " + self.pix_siz.get())
                addinfo.write("\n Exposure Time: " + (self.exp.get()))
                addinfo.write(
                    "\n Optical Magnification: "
                    + self.listboxa.get(self.listboxa.curselection())
                )

                addinfo.write("\n Comments:" + self.comments.get())

            addinfo.close()
            return

    def sav5(self):
        if len(self.items1) != 0 and len(self.items2) != 0:
            q = filedialog.asksaveasfilename(
                defaultextension=".txt",
                initialdir=" \\\\MIN-2835K4J\\C$\\CT Data\\",
                filetypes=[("text files", ".txt")],
                title="Pick a directory",
                initialfile="_CTUSERFORM.txt",
            )

            addinfo = open(q, "w")
            addinfo.write(" date: " + self.date.get())
            addinfo.write("\n IAC Project Identifier: " + self.pr_code.get())
            addinfo.write("\n Tomographer: " + self.tom.get())
            addinfo.write(
                "\n Equipment used: " + self.listbox4.get(self.listbox4.curselection())
            )
            addinfo.write("\n                  ")

            addinfo.write(
                "\n Project type: " + self.listbox0.get(self.listbox0.curselection())
            )
            if int(self.listbox0.curselection()[0]) == 0:
                addinfo.write("\n Curator name: " + self.curator.get())
                addinfo.write(
                    "\n Collection name: "
                    + self.listbox3.get(self.listbox3.curselection())
                )
                addinfo.write("\n Specimen name: " + self.specimen.get())
                addinfo.write("\n NHM accession number: " + self.accession.get())
            elif int(self.listbox0.curselection()[0]) != 0:
                addinfo.write("\n Curator name: " + "not relevant")
                addinfo.write("\n Collection name: " + "not relevant")
                addinfo.write("\n Sample type: " + self.spltyp.get())
                addinfo.write("\n NHM accession number: " + "not relevant")
            addinfo.write("\n                  ")

            addinfo.write("\n Name of your project: " + self.project_name.get())
            addinfo.write("\n Lead researcher: " + self.lead_researcher.get())
            if int(self.listbox2.curselection()[0]) != 6:
                addinfo.write(
                    "\n Affiliation: " + self.listbox2.get(self.listbox2.curselection())
                )
            elif int(self.listbox2.curselection()[0]) == 6:
                addinfo.write("\n Affiliation: " + self.sp_affil.get())
            if self.proj_name.lower() != self.existing_proj.lower():
                addinfo.write("\n Existing project: " + "No")
                addinfo.write("\n Funding source: " + self.funding.get())
                if self.var1.get() == 0:
                    addinfo.write("\n Confidentiality: " + "no")
                else:
                    addinfo.write("\n Confidentiality: " + "yes")
            elif self.proj_name.lower() == self.existing_proj.lower():
                addinfo.write("\n Existing project: " + "Yes")
            addinfo.write("\n                  ")

            if int(self.listbox2.curselection()[0]) == 1:
                addinfo.write(
                    "\n Metal target: "
                    + self.listbox1.get(self.listbox1.curselection())
                )
            elif int(self.listbox0.curselection()[0]) == 0:

                addinfo.write("\n Camera Binning: " + self.bin.get())
                addinfo.write(
                    "\n Source Filter" + self.listboxf.get(self.listboxf.curselection())
                )
                addinfo.write("\n Voltage: " + self.volt.get())
                addinfo.write("\n Current: " + self.amp.get())
                addinfo.write("\n Source-RA distance: " + self.src_dist.get())
                addinfo.write("\n Detector-RA distance: " + self.det_dist.get())
                addinfo.write("\n Projections: " + self.proj.get())
                addinfo.write("\n Pixel size: " + self.pix_siz.get())
                addinfo.write("\n Exposure Time: " + (self.exp.get()))
                addinfo.write(
                    "\n Optical Magnification: "
                    + self.listboxa.get(self.listboxa.curselection())
                )

                addinfo.write("\n Comments:" + self.comments.get())

            addinfo.close()
            return


def main():

    root = Tk()
    Demo1(root)
    root.mainloop()


if __name__ == "__main__":
    main()
