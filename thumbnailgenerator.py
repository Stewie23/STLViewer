#!/usr/bin/env python

import vtk

def createAutoThumb(filename,path):
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

def createManualThumb(filename,path):
    #thumbnailgenerator with user input
    pass
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


