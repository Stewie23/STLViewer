#!/usr/bin/env python

import vtk
from PIL import Image, ImageTk
class KeyPressInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):

    def __init__(self,renWin,filename,widget,parent=None):
        self.renWin = renWin
        self.widget = widget
        self.filename = filename
        self.parent = vtk.vtkRenderWindowInteractor()
        if(parent is not None):
            self.parent = parent

        self.AddObserver("KeyPressEvent",self.keyPress)

    def keyPress(self,obj,event):
        key = self.parent.GetKeySym()
        if key == "Return":
            WriteImage(str(self.filename)+".jpg", self.renWin, rgba=False)
            #also update the thumbnail widget and close the renderwindow
            image = Image.open("Thumbnails/"+str(self.filename)+".jpg")
            image = image.resize((150, 150), Image.ANTIALIAS)
            photo = ImageTk.PhotoImage(image)
            self.widget.mImage.image = photo#reference keeping
            self.widget.mImage.configure(image=photo) 

def createAutoThumb(filename,path):
    print(filename)
    colors = vtk.vtkNamedColors()

    # Set the background color.
    colors.SetColor("BkgColor", [26, 51, 102, 255])

    # create a rendering window and renderer
    ren = vtk.vtkRenderer()
    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(ren)
    renWin.OffScreenRenderingOn()

    # create source
    reader = vtk.vtkSTLReader()
    reader.SetFileName(path)

    # mapper
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(reader.GetOutputPort())

    # actor
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    # color the actor
    actor.GetProperty().SetColor(colors.GetColor3d("Grey"))

    # assign actor to the renderer
    ren.AddActor(actor)
    ren.SetBackground(colors.GetColor3d("BkgColor"))

    renWin.Render()
    WriteImage(filename+".jpg", renWin, rgba=False)

def createManualThumb(filename,path,widget):
    colors = vtk.vtkNamedColors()

    # Set the background color.
    colors.SetColor("BkgColor", [26, 51, 102, 255])

    # create a rendering window and renderer
    ren = vtk.vtkRenderer()
    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(ren)
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetInteractorStyle(KeyPressInteractorStyle(renWin,filename,widget,parent = iren))
    iren.SetRenderWindow(renWin)

    # create source
    reader = vtk.vtkSTLReader()
    reader.SetFileName(path)

    # mapper
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(reader.GetOutputPort())

    # actor
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    # color the actor
    actor.GetProperty().SetColor(colors.GetColor3d("Grey"))

    # assign actor to the renderer
    ren.AddActor(actor)
    ren.SetBackground(colors.GetColor3d("BkgColor"))
    iren.Initialize()
    renWin.Render()
    iren.Start()
   
def WriteImage(fileName, renWin, rgba=True):
    """
    Write the render window view to an image file.

    Image types supported are:
     BMP, JPEG, PNM, PNG, PostScript, TIFF.
    The default parameters are used for all writers, change as needed.

    :param fileName: The file name, if no extension then PNG is assumed.
    :param renWin: The render window.
    :param rgba: Used to set the buffer type.
    :return:
    """

    import os

    #check für /Thumbnails folder

    if os.path.exists("Thumbnails") == True:
        pass
    else:
        os.mkdir("Thumbnails")

    if fileName:
        writer = vtk.vtkJPEGWriter()
        windowto_image_filter = vtk.vtkWindowToImageFilter()
        windowto_image_filter.SetInput(renWin)
        windowto_image_filter.SetScale(1)  # image quality
        if rgba:
            windowto_image_filter.SetInputBufferTypeToRGBA()
        else:
            windowto_image_filter.SetInputBufferTypeToRGB()
            # Read from the front buffer.
            windowto_image_filter.ReadFrontBufferOff()
            windowto_image_filter.Update()

        writer.SetFileName("Thumbnails/"+fileName)
        writer.SetInputConnection(windowto_image_filter.GetOutputPort())
        writer.Write()
    else:
        raise RuntimeError('Need a filename.')