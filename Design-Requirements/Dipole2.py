# ============================================================
# HFSS IronPython — Planar Dipole over Tunable Backing Slab
# Dynamic vars: epsr_re, epsr_im, mur_re, mur_im, sigma, h_lam
# Far-field (Infinite Sphere) + Optimetrics param sweeps
# ============================================================

import ScriptEnv
ScriptEnv.Initialize("Ansoft.ElectronicsDesktop")

oDesktop = ScriptEnv.GetDesktop()
oDesktop.RestoreWindow()

# ---------- Project / Design ----------
oProject = oDesktop.NewProject()
oProject.InsertDesign("HFSS", "Dipole_Back_Ref", "DrivenModal", "")
oDesign  = oProject.SetActiveDesign("Dipole_Back_Ref")
oEditor  = oDesign.SetActiveEditor("3D Modeler")
oDefinitionManager = oProject.GetDefinitionManager()

# ---------- Units ----------
oEditor.SetModelUnits(["NAME:Units Parameter","Units:=","mm","Rescale:=",False])

# ---------- Design Variables ----------
oDesign.ChangeProperty([
    "NAME:AllTabs",
    ["NAME:LocalVariableTab",
        ["NAME:PropServers","LocalVariables"],
        ["NAME:NewProps",
            # RF & geometry fundamentals
            ["NAME:f0",       "PropType:=","VariableProp","UserDef:=",True,"Value:=","10MHz"],
            ["NAME:lambda0",  "PropType:=","VariableProp","UserDef:=",True,"Value:=","(299792458m_per_s)/f0"],
            ["NAME:h_lam",    "PropType:=","VariableProp","UserDef:=",True,"Value:=","0.25"],
            ["NAME:h",        "PropType:=","VariableProp","UserDef:=",True,"Value:=","h_lam*lambda0"],

            ["NAME:l_factor", "PropType:=","VariableProp","UserDef:=",True,"Value:=","1.0"], # 0.95–1.0
            ["NAME:L_dip",    "PropType:=","VariableProp","UserDef:=",True,"Value:=","l_factor*lambda0/2"],
            ["NAME:w_dip",    "PropType:=","VariableProp","UserDef:=",True,"Value:=","2mm"],
            ["NAME:t_dip",    "PropType:=","VariableProp","UserDef:=",True,"Value:=","0.5mm"],
            ["NAME:gap",      "PropType:=","VariableProp","UserDef:=",True,"Value:=","2mm"],

            # Backing slab planform & thickness
            ["NAME:gp_x",     "PropType:=","VariableProp","UserDef:=",True,"Value:=","1.5*lambda0"],
            ["NAME:gp_z",     "PropType:=","VariableProp","UserDef:=",True,"Value:=","1.5*lambda0"],
            ["NAME:gp_t",     "PropType:=","VariableProp","UserDef:=",True,"Value:=","5mm"],

            # Air padding
            ["NAME:air_pad",  "PropType:=","VariableProp","UserDef:=",True,"Value:=","0.5*lambda0"],

            # Material knobs (dynamic)
            ["NAME:epsr_re",  "PropType:=","VariableProp","UserDef:=",True,"Value:=","13"],
            ["NAME:epsr_im",  "PropType:=","VariableProp","UserDef:=",True,"Value:=","0"],
            ["NAME:mur_re",   "PropType:=","VariableProp","UserDef:=",True,"Value:=","1"],
            ["NAME:mur_im",   "PropType:=","VariableProp","UserDef:=",True,"Value:=","0"],
            ["NAME:sigma",    "PropType:=","VariableProp","UserDef:=",True,"Value:=","5e-3S_per_m"]
        ]
    ]
])

# ---------- Backing Material (complex εr/μr + σ) ----------
# Note: 'j' is valid imaginary unit in AEDT expressions; switch to 'i' if needed.
try:
    oDefinitionManager.AddMaterial([
        "NAME:BackerMat",
        "CoordinateSystemType:=","Cartesian",
        "BulkOrSurfaceType:=",1,
        ["NAME:PhysicsTypes","set:=",["Electromagnetic"]],
        "permittivity:=","epsr_re - j*(epsr_im + sigma/(2*pi*f0*8.854187817e-12F_per_m))",
        "permeability:=","mur_re - j*mur_im",
        "conductivity:=","sigma"
    ])
except:
    oDefinitionManager.EditMaterial("BackerMat",[
        "NAME:BackerMat",
        "CoordinateSystemType:=","Cartesian",
        "BulkOrSurfaceType:=",1,
        ["NAME:PhysicsTypes","set:=",["Electromagnetic"]],
        "permittivity:=","epsr_re - j*(epsr_im + sigma/(2*pi*f0*8.854187817e-12F_per_m))",
        "permeability:=","mur_re - j*mur_im",
        "conductivity:=","sigma"
    ])

# ---------- Geometry: Planar Dipole (along +X, centered at origin) ----------
# Left arm: from -L_dip/2 to -gap/2
oEditor.CreateBox(
    ["NAME:BoxParameters",
     "XPosition:=","-(L_dip/2)",
     "YPosition:=","-t_dip/2",
     "ZPosition:=","-w_dip/2",
     "XSize:=","(L_dip/2 - gap/2)",
     "YSize:=","t_dip",
     "ZSize:=","w_dip"],
    ["NAME:Attributes","Name:=","DipoleLeft","MaterialName:=","copper","SolveInside:=",False]
)

# Right arm: from +gap/2 to +L_dip/2
oEditor.CreateBox(
    ["NAME:BoxParameters",
     "XPosition:=","gap/2",
     "YPosition:=","-t_dip/2",
     "ZPosition:=","-w_dip/2",
     "XSize:=","(L_dip/2 - gap/2)",
     "YSize:=","t_dip",
     "ZSize:=","w_dip"],
    ["NAME:Attributes","Name:=","DipoleRight","MaterialName:=","copper","SolveInside:=",False]
)

# Port sheet across the gap at x=0 (YZ plane); use nonzero width/height
oEditor.CreateRectangle(
    ["NAME:RectangleParameters",
     "IsCovered:=",True,
     "XStart:=","0mm",
     "YStart:=","-t_dip/2",
     "ZStart:=","-w_dip/2",
     "Width:=","t_dip",          # along +Y
     "Height:=","w_dip",         # along +Z
     "WhichAxis:=","X"],
    ["NAME:Attributes","Name:=","LumpPortSheet","MaterialName:=","vacuum","SolveInside:=",True]
)

# ---------- Backing (reference) slab ----------
# Top face at y = -h (i.e., directly "behind" dipole midpoint by distance h)
oEditor.CreateBox(
    ["NAME:BoxParameters",
     "XPosition:=","-gp_x/2",
     "YPosition:=","-(h + gp_t)",
     "ZPosition:=","-gp_z/2",
     "XSize:=","gp_x",
     "YSize:=","gp_t",
     "ZSize:=","gp_z"],
    ["NAME:Attributes","Name:=","BackerSlab","MaterialName:=","BackerMat","SolveInside:=",True]
)

# ---------- Airbox & Radiation ----------
oEditor.CreateBox(
    ["NAME:BoxParameters",
     "XPosition:=","-(gp_x/2 + air_pad)",
     "YPosition:=","-(h + gp_t + air_pad)",
     "ZPosition:=","-(gp_z/2 + air_pad)",
     "XSize:=","gp_x + 2*air_pad",
     "YSize:=","h + gp_t + t_dip + 2*air_pad",
     "ZSize:=","gp_z + 2*air_pad"],
    ["NAME:Attributes","Name:=","AirBox","MaterialName:=","air","SolveInside:=",True]
)

oBnd = oDesign.GetModule("BoundarySetup")
air_faces = oEditor.GetFaceIDs("AirBox")
oBnd.AssignRadiation(["NAME:Rad1","Faces:=", air_faces])

# ---------- Lumped Port (face-based, defined current line) ----------
port_faces = oEditor.GetFaceIDs("LumpPortSheet")
# Use the sole face of the sheet
port_face = [int(port_faces[0])] if isinstance(port_faces[0], (str, unicode)) if hasattr(__builtins__,'unicode') else [int(port_faces[0])]
# Define a current line across the gap thickness (Y direction)
oBnd.AssignLumpedPort(
    ["NAME:Port1",
     "Faces:=", port_face,
     "DoDeembed:=", False,
     "RenormalizeAllTerminals:=", True,
     "Impedance:=","50ohm",
     ["NAME:CurrentLine",
      "Start:=", ["0mm","-t_dip/2","0mm"],
      "End:=",   ["0mm","t_dip/2","0mm"]
     ]
    ]
)

# ---------- Analysis Setup + Sweep ----------
oAn = oDesign.GetModule("AnalysisSetup")
oAn.InsertSetup("HfssDriven",
    ["NAME:Setup1",
     "Frequency:=","f0",
     "MaxDeltaS:=",0.02,
     "MaximumPasses:=",15,
     "MinimumPasses:=",2,
     "MinimumConvergedPasses:=",1,
     "PercentRefinement:=",30,
     "SaveFields:=",False,
     "SaveRadFields:=",True,
     "IsEnabled:=",True]
)

oAn.InsertFrequencySweep("Setup1",
    ["NAME:Sweep1",
     "IsEnabled:=",True,
     "RangeType:=","LinearStep",
     "RangeStart:=","0.9*f0",
     "RangeEnd:=","1.1*f0",
     "RangeStep:=","0.02*f0",
     "Type:=","Interpolating",
     "SaveFields:=",False,
     "SaveRadFields:=",True,
     "UseDerivativeConvergence:=",True,
     "InterpTolerance:=",0.5,
     "InterpMaxSolns:=",250,
     "InterpMinSolns:=",0,
     "InterpMinSubranges:=",1]
)

# ---------- Far-Field (Infinite Sphere) ----------
oRad = oDesign.GetModule("RadField")
oRad.InsertInfiniteSphereSetup(
    ["NAME:InfSphere1",
     "UseCustomRadiationSurface:=", False,
     "ThetaStart:=","0deg","ThetaStop:=","180deg","ThetaStep:=","2deg",
     "PhiStart:=","0deg","PhiStop:=","360deg","PhiStep:=","5deg"]
)

# ---------- 3D Polar Far-Field Report ----------
oRpt = oDesign.GetModule("ReportSetup")
oRpt.CreateReport(
    "Gain3D_Total",
    "Far Fields",
    "3D Polar Plot",
    "Setup1 : Sweep1",
    ["Context:=","InfSphere1","Domain:=","Sweep"],
    ["Theta:=",["All"], "Phi:=",["All"], "Freq:=",["f0"]],
    ["GainTotal"],
    []
)

# ---------- Optimetrics: parameter sweeps for animation ----------
oOpt = oDesign.GetModule("Optimetrics")

def insert_parametric(name, pairs, setupsel="Setup1", sweepname="Sweep1"):
    vars_block = ["NAME:Variables"]
    for v, data in pairs:
        vars_block.append(
            ["NAME:Variable","Variable:=",v,"Data:=",data,"OffsetF1:=",False,"Synchronize:=",0]
        )
    oOpt.InsertSetup("Parametric",[
        "NAME:"+name,
        "IsEnabled:=",True,
        ["NAME:ProdOptiSetupDataV2","SaveFields:=",False,"CopyMesh:=",True],
        ["NAME:StartingPoint"],
        vars_block,
        ["NAME:Sweeps",["NAME:SweepDefinition","Variable:=","Freq","Data:=","All","OffsetF1:=",False]],
        "Setup:=",setupsel,
        "Sweep:=",sweepname
    ])

# Ranges consistent with your MATLAB notes:
insert_parametric("Param_h_lam", [("h_lam","LIST(0.01,0.05,0.10,0.15,0.20,0.25)")])
insert_parametric("Param_eps",   [("epsr_re","LIST(5,13,30,50,81)"),("epsr_im","LIST(0,0.5,1,2,4)")])
insert_parametric("Param_mu",    [("mur_re","LIST(1,10,100,300,600)"),("mur_im","LIST(0,25,50,100,150,200)")])
insert_parametric("Param_sigma", [("sigma","LIST(0.001S_per_m,0.005S_per_m,0.05S_per_m,0.5S_per_m,5S_per_m)")])

# View fit
oEditor.FitAll()

# (Optional) Run nominal solve:
# oDesign.AnalyzeAll()
# ============================================================
# End of script
# ============================================================
