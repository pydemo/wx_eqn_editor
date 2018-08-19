#!/usr/bin/env python

"""
Test of embedding matplotlib, and using it to render a mathematical equation.

Original demo by Chris Barker   2010-12-15
Ergonomic, cropping and file saving additions by Ray Pasco     2010-12-15

Tested using :

Windows   6.1.7600   [ Win7 64-bit running on an AMD CPU ]
Python    2.6.5 (r265:79096, Mar 19 2010, 21:48:26) [MSC v.1500 32 bit (Intel)]
Wx         2.8.11.0
Matplotlib 1.0.0
PIL        1.1.7
"""

import time

import wx


class my_short_cut(object):
    def __init__(self, text, ord_str, label=None, id=None, accels=wx.ACCEL_CTRL):
        self.text = text
        self.ord_str = ord_str
        self.id = id
        if label is None:
            label = text
        self.label = label
        self.accels = accels


# These imports take an incredibly long time. [ ~1.8 seconds ]
# Let the user know this is normal and expected.
print('\n----  Importing Matplotlib and Related Modules...')
start = time.clock() # measure the import time
#
import matplotlib
import matplotlib.pyplot as plt

#plt.rc('text', usetex=True)
#plt.rc('text.latex', preamble=r'\usepackage{/Users/kraussry/gdrive_teaching/general_teaching/lecture_templates/mydefs}')
        
matplotlib.use( 'WXAgg' )   # AggDraw for wxPython.
import matplotlib.figure
import matplotlib.backends.backend_wxagg
#
end = time.clock()
print('      Import Time =', end-start, 'seconds')

#------------------------------------------------------------------------------

class MathPanel( wx.Panel ) :
    """
    The MathPanel is a very simple panel with just and MPL figure on it,
    it will automatically render text in the middle of the figure
    """

    def __init__( self, parent ) :

        wx.Panel.__init__( self, parent=parent, size=(500, 200) )

        #-----

        # initialize matplotlib stuff.
        #
        # To make all new figure backgrounds be initialized to white
        # edit the file [ \Lib\site-packages\matplotlib\mpl-data\matplotlibrc ]
        # Find line [ figure.facecolor : 0.75 ] in section [ ### FIGURE ] and change it to
        # [ figure.facecolor : 1.00 ]. Who would want a gray background color by default !?
        #
        # Create the "figure" and set its background color to white.
        self.figure = matplotlib.figure.Figure( None, facecolor='white' )
        self.canvas = matplotlib.backends.backend_wxagg.FigureCanvasWxAgg(  \
                          self, -1, self.figure )

        self._SetSize()
        self.Bind( wx.EVT_SIZE, self._SetSize )

        self.TeX = ''
        self.font_size = 20
        self.RenderEquation()

    #end __init__

    #----------------------------------

    def SetTeX( self, str ) :

        self.TeX = '$%s$' % (str)
        self.RenderEquation()

    #----------------------------------

    def RenderEquation( self ) :

        self.renderError = False        # Can save to file only if False

        try :
            self.figure.clear()
            self.figure.text( 0.05, 0.5, self.TeX, size=self.font_size )
            self.canvas.draw()

        except matplotlib.pyparsing.ParseFatalException :

            self.renderError = True     # Don't save the Tex error message to a file !
            self.figure.clear()
            self.figure.text( 0.05, 0.5, 'Parsing Error in MathTeX', size=self.font_size )
            self.canvas.draw()

        #end try

    #end def

    #----------------------------------

    def _SetSize( self, evt=None ) :

        pixels = self.GetSize()
        self.SetSize( pixels )
        self.canvas.SetSize( pixels )

        dpi = self.figure.get_dpi()
        self.figure.set_size_inches( float( pixels[0] ) / dpi,
                                     float( pixels[1] ) / dpi )
    #end def

#------------------------------------------------------------------------------

class MathFrame( wx.Frame ) :

    def __init__( self ) :

        wx.Frame.__init__( self, None, -1, pos=(10, 10),
                           title='Matplotlib Math EquationRenderer Test'  )
        self.ClientSize = (800, 275)

        # Frames need an initial panel to provide tab traversal and
        # cross-platform background color capabilities.
        frmPanel = wx.Panel( self )

        #-----

        self.math_panel = MathPanel( frmPanel )

        self.input_box = wx.TextCtrl( frmPanel, size=(500, -1) )
        self.input_box.SetFocus()
        self.input_box.Font = wx.Font( 10,
                                       wx.FONTFAMILY_TELETYPE,
                                       wx.FONTSTYLE_NORMAL,
                                       wx.FONTWEIGHT_NORMAL )
        self.input_box.Bind( wx.EVT_TEXT, self.OnText )

        # Set a default equation. Show some fancy math symbols.
        equation = r'Goober = {\min(\int\ (\ {\delta{(\ \pi{}*\frac{\sum(\ a+\O\o\l\S\P\L\{b\}\ )\ } {( c-d )}})}\ )}'
        self.input_box.Value = ""#equation

        label_stTxt = wx.StaticText( frmPanel, label='Type some TeX here :' )

        saveBtn = wx.Button( frmPanel, label='Save Equation to File' )
        saveBtn.Bind( wx.EVT_LEFT_DOWN, self.OnSaveToFileBtn )

        exitBtn = wx.Button( frmPanel, label='Exit' )
        exitBtn.Bind( wx.EVT_LEFT_DOWN, self.OnExit )

        #-----  Layout

        frmPnl_vertSzr = wx.BoxSizer( wx.VERTICAL )

        frmPnl_vertSzr.Add( label_stTxt,     proportion=0, flag=wx.TOP|wx.LEFT, border=5 )
        frmPnl_vertSzr.Add( self.input_box,  proportion=0, flag=wx.GROW|wx.ALL, border=5 )
        frmPnl_vertSzr.Add( self.math_panel, proportion=1, flag=wx.GROW )
        frmPnl_vertSzr.Add( saveBtn, proportion=0,
                            flag=wx.ALIGN_CENTER|wx.BOTTOM|wx.TOP, border=10 )
        frmPnl_vertSzr.Add( exitBtn, proportion=0,
                            flag=wx.ALIGN_CENTER|wx.BOTTOM,        border=10 )

        frmPanel.SetSizerAndFit( frmPnl_vertSzr )

        self.Bind(wx.EVT_ACTIVATE, self.OnActivate)
        
        menuBar = wx.MenuBar()
        fileMenu = wx.Menu()
        quitID = wx.NewId()
        quitMenuItem = fileMenu.Append(quitID, "Quit", "Quit the application")
        menuBar.Append(fileMenu, "&File")
        self.Bind(wx.EVT_MENU, self.OnExit, quitMenuItem)


        # Edit/copy
        editMenu = wx.Menu()
        copyID = wx.NewId()
        copyItem = editMenu.Append(copyID, "&Copy", "Copy entire equation to clipboard")
        self.Bind(wx.EVT_MENU, self.OnCopy, copyItem)

        menuBar.Append(editMenu, "&Edit")

        # 345 keyboard short cuts
        menu345 = wx.Menu()
        omegaID = wx.NewId()
        omegaItem = menu345.Append(omegaID, "omega_n", "Insert omega_n")
        self.Bind(wx.EVT_MENU, self.OnOmega, omegaItem)


        zetaID = wx.NewId()
        zetaItem = menu345.Append(zetaID, "zeta", "Insert zeta")
        self.Bind(wx.EVT_MENU, self.OnZeta, zetaItem)

        fracID = wx.NewId()
        fracItem = menu345.Append(fracID, "fraction", "Insert fraction")
        self.Bind(wx.EVT_MENU, self.OnFrac, fracItem)

        second_order_ID = wx.NewId()
        second_order_Item = menu345.Append(second_order_ID, "second_order TF", "Insert second_order TF")
        self.Bind(wx.EVT_MENU, self.OnSecondOrder, second_order_Item)

        so_str = '\\frac{\\omega_n^2}{s^2+2\\zeta \\omega_n s + \\omega_n^2}'
        
        accel_list = [my_short_cut('G(s)','g'), \
                      my_short_cut('G(s) = ','g', \
                                   accels=wx.ACCEL_CTRL|wx.ACCEL_SHIFT), \
                      my_short_cut('\\frac{p}{s+p}','1','first order TF'), \
                      my_short_cut('\\frac{1}{s}','s', 'step input (1/s)'), \
                      my_short_cut('\\left(','9'), \
                      my_short_cut('\\right)','0'), \
                      my_short_cut('\\left[','['), \
                      my_short_cut('\\right]',']'), \
                      my_short_cut(so_str, '2', 'second order (no G)')
                     ]
        
        self.id_dict_345 = {}
        for item in accel_list:
            new_id = wx.NewId()
            item.id = new_id
            self.id_dict_345[new_id] = item
            newItem = menu345.Append(new_id, item.label, "Insert %s" % item.text)
            self.Bind(wx.EVT_MENU, self.OnDictInsert, newItem)
            

        menuBar.Append(menu345, "&345")

        ## Set Menu Bar
        self.SetMenuBar(menuBar)

        # set up accelerators
        accelEntries = []
        accelEntries.append((wx.ACCEL_CTRL, ord('Q'), quitID))
        accelEntries.append((wx.ACCEL_CTRL|wx.ACCEL_SHIFT, ord('w'), omegaID))
        accelEntries.append((wx.ACCEL_CTRL|wx.ACCEL_SHIFT, ord('z'), zetaID))
        accelEntries.append((wx.ACCEL_CTRL|wx.ACCEL_SHIFT, ord('f'), fracID))        
        accelEntries.append((wx.ACCEL_CTRL|wx.ACCEL_SHIFT, ord('c'), copyID))
        accelEntries.append((wx.ACCEL_CTRL|wx.ACCEL_SHIFT, ord('2'), second_order_ID))        
        #accelEntries.append((wx.ACCEL_CTRL, ord('S'), xrc.XRCID("file_save_menu")))

        for item in accel_list:
            accelEntries.append((item.accels, \
                                 ord(item.ord_str), item.id))        

        accelTable  = wx.AcceleratorTable(accelEntries)
        self.SetAcceleratorTable(accelTable)


        # Final Set Up
        self.Center()
        #print('called set focus on input box')
        #self.SetFocus()
        #self.input_box.SetFocus()


    #end __init__

    def OnActivate(self, evt):
        print('in OnActivate')
        self.input_box.SetFocus()
        
    #----------------------------------

    def OnText( self, evt ) :
        eqn_text = self.input_box.Value
        if eqn_text:
            self.math_panel.SetTeX(eqn_text)

    #----------------------------------

    def OnExit( self, evt ) :

        self.Close()


    def OnDictInsert(self, evt):
        my_sc = self.id_dict_345[evt.GetId()]
        self.input_box.WriteText(my_sc.text)
        
        
    def OnOmega(self, evt):
        #print('in OnOmega')
        self.input_box.WriteText('\\omega_n')


    def OnZeta(self, evt):
        #print('in OnOmega')
        self.input_box.WriteText('\\zeta')


    def OnFrac(self, evt):
        #print('in OnOmega')
        self.input_box.WriteText('\\frac{}{}')


    def OnSecondOrder(self, evt):
        self.input_box.WriteText(r'G(s) = \frac{\omega_n^2}{s^2 + 2 \zeta \omega_n s + \omega_n^2}')


    def OnCopy(self, evt):
        eqn_text = self.input_box.Value
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(wx.TextDataObject(eqn_text))
            wx.TheClipboard.Close()
        else:
            print("failed to open clipboard")
            
        
    #----------------------------------

    def OnSaveToFileBtn( self, event ) :

        if not self.math_panel.renderError :

            filename = 'Rendered_Equation.png'
            self.math_panel.figure.savefig( filename, dpi=300 )
            print('\n----  Equation Graphic Saved to File [ %s ]' % filename)

            # See if the PIL package is installed.
            pilIsInstalled = True
            try :
                # Try to crop the image to its near-minimum extent.
                import Image        # PIL (Python Image Library)
                import ImageChops   # Image Channel Operations library
                import ImageStat    # Image Statistics library
                import ImageOps     # Various whole image operations.

            except :
                pilIsInstalled = False   # Image will not get auto-cropped.
            #end try

            if pilIsInstalled :      # Auto-crop the image.
                pilImg = Image.open( filename )

                # Find the ordinates of the minimally enclosing bounding box.
                #
                # Create a simplified and inverted version of the original image to examine.
                invertedImage = ImageChops.invert( pilImg.convert( 'L' ) )   # BG must be black to examine.

                # Get the bounding box's ordinates. Works on any image with a black background.
                box = invertedImage.getbbox()
                pilImg = pilImg.crop( box )

                # Add back a thin border padding. This is arbitrary, but seems reasonable.
                pilImg = ImageOps.expand( pilImg, border=10, fill=(255, 255, 255) )

                # Save the image to a disk file. Only PNG and TIFF formats are non-destructive.
                pilImg.save( filename )
                print('      Cropped Equation Graphic Saved')

            #end if

        else :
            print('\n---- Tex Rendering Error:  Figure Image NOT SAVED to a File.')
        #end if

    #end def

#end MathFrame class

#==============================================================================

if __name__ == '__main__' :

    # What packages are installed ?
    import os, sys, platform
    print()
    if os.name == 'nt' :
        print('Windows  ', platform.win32_ver()[1])
    else :
        print('Platform ', platform.system())
    #end if
    print('Python   ', sys.version)

    addon_pkgs = [ ('Wx        ', 'wx.VERSION_STRING'),
                   ('Matplotlib', 'matplotlib.__version__'), ]

    try :
        import Image        # Doesn't need to be installed.
        pilStr = 'PIL       '
        pilAddonStr = 'Image.VERSION'
        addon_pkgs.append( (pilStr      , pilAddonStr) )
    except :
        pass
    #end try

    for addonStr, attribute in addon_pkgs :
        try :
            print(addonStr, eval( attribute ))
        except NameError :
            print()
        #end try
    #end for
    print()

    #----

    app = wx.App( redirect=False )
    appFrame = MathFrame().Show()
    app.MainLoop()

#end if
