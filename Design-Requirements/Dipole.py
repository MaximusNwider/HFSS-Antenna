# ============================================================
# HFSS IronPython Script — Planar Dipole over Tunable Backing
# Spacing h = (h_lam)*lambda0 behind dipole midpoint
# Dynamic variables: epsr_re, epsr_im, mur_re, mur_im, sigma, h_lam
# Optimetrics sweeps + 3D far-field report for animation
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
oEditor.SetModelUnits(
    [
        "NAME:Units Parameter",
        "Units:=", "mm",
        "Rescale:=", False
    ]
)

# ---------- Design Variables ----------
# Base RF
oDesign.ChangeProperty(
    [
        "NAME:AllTabs",
        [
            "NAME:LocalVariableTab",
            ["NAME:PropServers", "LocalVariables"],
            [
                "NAME:NewProps",
                ["NAME:f0",        "PropType:=", "VariableProp", "UserDef:=", True, "Value:=", "10MHz"],
                ["NAME:c0",        "PropType:=", "VariableProp", "UserDef:=", True, "Value:=", "299792458m_per_s"],
                ["NAME:mu0",       "PropType:=", "VariableProp", "UserDef:=", True, "Value:=", "4*pi*1e-7H_per_m"],
                ["NAME:eps0",      "PropType:=", "VariableProp", "UserDef:=", True, "Value:=", "1/(mu0*(c0^2))F_per_m"],
                ["NAME:omega0",    "PropType:=", "VariableProp", "UserDef:=", True, "Value:=", "2*pi*f0"],
                ["NAME:lambda0",   "PropType:=", "VariableProp", "UserDef:=", True, "Value:=", "c0/f0"],

                # Dipole geometry (defaults; tweak as you like)
                ["NAME:h_lam",     "PropType:=", "VariableProp", "UserDef:=", True, "Value:=", "0.25"], # h/λ
                ["NAME:h",         "PropType:=", "VariableProp", "UserDef:=", True, "Value:=", "h_lam*lambda0"],

                ["NAME:l_factor",  "PropType:=", "VariableProp", "UserDef:=", True, "Value:=", "1.0"],   # 1.0 = ideal half-wave; use ~0.95 for end-effects
                ["NAME:L_dip",     "PropType:=", "VariableProp", "UserDef:=", True, "Value:=", "l_factor*lambda0/2"],
                ["NAME:w_dip",     "PropType:=", "VariableProp", "UserDef:=", True, "Value:=", "2mm"],
                ["NAME:t_dip",     "PropType:=", "VariableProp", "UserDef:=", True, "Value:=", "0.5mm"],
                ["NAME:gap",       "PropType:=", "VariableProp", "UserDef:=", True, "Value:=", "2mm"],

                # Backing/reference slab size & thickness
                ["NAME:gp_x",      "PropType:=", "VariableProp", "UserDef:=", True, "Value:=", "1.5*lambda0"],
                ["NAME:gp_z",      "PropType:=", "VariableProp", "UserDef:=", True, "Value:=", "1.5*lambda0"],
                ["NAME:gp_t",      "PropType:=", "VariableProp", "UserDef:=", True, "Value:=", "5mm"],

                # Airbox padding
                ["NAME:air_pad",   "PropType:=", "VariableProp", "UserDef:=", True, "Value:=", "0.5*lambda0"],

                # Material knobs (dynamic)
                # Use epsr_re - j*(epsr_im + sigma/(omega0*eps0)) if you want conduction included in imag(εr).
                ["NAME:epsr_re",   "PropType:=", "VariableProp", "UserDef:=", True, "Value:=", "13"],
                ["NAME:epsr_im",   "PropType:=", "VariableProp", "UserDef:=", True, "Value:=", "0"],

                ["NAME:mur_re",    "PropType:=", "VariableProp", "UserDef:=", True, "Value:=", "1"],
                ["NAME:mur_im",    "PropType:=", "VariableProp", "UserDef:=", True, "Value:=", "0"],

                ["NAME:sigma",     "PropType:=", "VariableProp", "UserDef:=", True, "Value:=", "5e-3S_per_m"]
            ]
        ]
    ]
)

# ---------- Custom Material for Backing Slab ----------
# Complex epsilon/mu with conduction; switch j->i if your AEDT expects 'i'
try:
    oDefinitionManager.AddMaterial(
        [
            "NAME:BackerMat",
            "CoordinateSystemType:=", "Cartesian",
            "BulkOrSurfaceType:=", 1,
            [
                "NAME:PhysicsTypes",
                "set:=", ["Electromagnetic"]
            ],
            "permittivity:=", "epsr_re - j*(epsr_im + sigma/(omega0*eps0))",
            "permeability:=", "mur_re - j*mur_im",
            "conductivity:=", "sigma"
        ]
    )
except:
    # If material exists, update it
    oDefinitionManager.EditMaterial(
        "BackerMat",
        [
            "NAME:BackerMat",
            "CoordinateSystemType:=", "Cartesian",
            "BulkOrSurfaceType:=", 1,
            [
                "NAME:PhysicsTypes",
                "set:=", ["Electromagnetic"]
            ],
            "permittivity:=", "epsr_re - j*(epsr_im + sigma/(omega0*eps0))",
            "permeability:=", "mur_re - j*mur_im",
            "conductivity:=", "sigma"
        ]
    )

# ---------- Geometry: Planar Dipole ----------
# Oriented along +X, centered at origin, thickness along Y, width along Z
# Two metal arms separated by 'gap'; each arm length = L_dip/2 - gap/2
oEditor.CreateBox(
    [
        "NAME:BoxParameters",
        "XPosition:=", "-(gap/2 + (L_dip/2 - gap/2))",             # = -L_dip/2
        "YPosition:=", "-t_dip/2",
        "ZPosition:=", "-w_dip/2",
        "XSize:=", "(L_dip/2 - gap/2)",
        "YSize:=", "t_dip",
        "ZSize:=", "w_dip"
    ],
    [
        "NAME:Attributes",
        "Name:=", "DipoleLeft",
        "MaterialName:=", "copper",
        "SolveInside:=", False
    ]
)

oEditor.CreateBox(
    [
        "NAME:BoxParameters",
        "XPosition:=", "gap/2",
        "YPosition:=", "-t_dip/2",
        "ZPosition:=", "-w_dip/2",
        "XSize:=", "(L_dip/2 - gap/2)",
        "YSize:=", "t_dip",
        "ZSize:=", "w_dip"
    ],
    [
        "NAME:Attributes",
        "Name:=", "DipoleRight",
        "MaterialName:=", "copper",
        "SolveInside:=", False
    ]
)

# Port sheet across the gap at x=0 (YZ plane)
oEditor.CreateRectangle(
    [
        "NAME:RectangleParameters",
        "IsCovered:=", True,
        "XStart:=", "0mm",
        "YStart:=", "-t_dip/2",
        "ZStart:=", "-w_dip/2",
        "Width:=", "0mm",              # zero width -> YZ plane
        "Height:=", "w_dip",
        "WhichAxis:=", "X"
    ],
    [
        "NAME:Attributes",
        "Name:=", "LumpPortSheet",
        "MaterialName:=", "vacuum",
        "SolveInside:=", True
    ]
)

# ---------- Backing / Reference Slab ----------
# Centered below (negative Y) by distance h; its TOP face sits at y = -h
oEditor.CreateBox(
    [
        "NAME:BoxParameters",
        "XPosition:=", "-gp_x/2",
        "YPosition:=", "-(h + gp_t)",       # bottom = -(h + gp_t)
        "ZPosition:=", "-gp_z/2",
        "XSize:=", "gp_x",
        "YSize:=", "gp_t",                   # thickness
        "ZSize:=", "gp_z"
    ],
    [
        "NAME:Attributes",
        "Name:=", "BackerSlab",
        "MaterialName:=", "BackerMat",
        "SolveInside:=", True
    ]
)

# ---------- Airbox & Radiation Boundary ----------
# Pad everything with 'air_pad' on all sides
oEditor.CreateBox(
    [
        "NAME:BoxParameters",
        "XPosition:=", "-(gp_x/2 + air_pad)",
        "YPosition:=", "-(h + gp_t + air_pad)",
        "ZPosition:=", "-(gp_z/2 + air_pad)",
        "XSize:=", "gp_x + 2*air_pad",
        "YSize:=", "(h + gp_t) + t_dip/2 + air_pad + air_pad",  # reaches above dipole slightly + padding
        "ZSize:=", "gp_z + 2*air_pad"
    ],
    [
        "NAME:Attributes",
        "Name:=", "AirBox",
        "MaterialName:=", "air",
        "SolveInside:=", True
    ]
)

# Subtract inner solids from air? (not necessary for radiation boundary; we keep all, then assign rad on AirBox)
# Assign Radiation to outer faces of AirBox
oModuleBnd = oDesign.GetModule("BoundarySetup")
# Pick AirBox faces by object name filter
airbox_faces = oEditor.GetFaceIDs("AirBox")
oModuleBnd.AssignRadiation(
    [
        "NAME:Rad1",
        "Faces:=", airbox_faces
    ]
)

# ---------- Excitation: Lumped Port ----------
# Assign lumped port on the sheet across the gap
oModuleBnd.AssignLumpedPort(
    [
        "NAME:Port1",
        "Objects:=", ["LumpPortSheet"],
        "RenormalizeAllTerminals:=", True,
        "DoDeembed:=", False,
        "Impedance:=", "50ohm",
        "TerminalType:=", "Floating"   # allows sheet excitation between the two arms
    ]
)

# ---------- Analysis Setup ----------
oModuleAnl = oDesign.GetModule("AnalysisSetup")
oModuleAnl.InsertSetup("HfssDriven",
    [
        "NAME:Setup1",
        "Frequency:=", "f0",
        "PortsOnly:=", False,
        "MaxDeltaS:=", 0.02,
        "UseMatrixConv:=", False,
        "MaximumPasses:=", 15,
        "MinimumPasses:=", 2,
        "MinimumConvergedPasses:=", 1,
        "PercentRefinement:=", 30,
        "IsEnabled:=", True
    ]
)

# Optional sweep (narrow band around f0 for pattern smoothness)
oModuleAnl.InsertFrequencySweep("Setup1",
    [
        "NAME:Sweep1",
        "IsEnabled:=", True,
        "RangeType:=", "LinearStep",
        "RangeStart:=", "0.9*f0",
        "RangeEnd:=", "1.1*f0",
        "RangeStep:=", "0.02*f0",
        "Type:=", "Interpolating",
        "SaveFields:=", False,
        "SaveRadFields:=", True,
        "UseDerivativeConvergence:=", True,
        "InterpTolerance:=", 0.5,
        "InterpMaxSolns:=", 250,
        "InterpMinSolns:=", 0,
        "InterpMinSubranges:=", 1
    ]
)

# ---------- Far-Field: Infinite Sphere ----------
oModuleRad = oDesign.GetModule("RadField")
oModuleRad.InsertInfiniteSphereSetup(
    [
        "NAME:InfSphere1",
        "UseCustomRadiationSurface:=", False,
        "ThetaStart:=", "0deg",
        "ThetaStop:=", "180deg",
        "ThetaStep:=", "2deg",
        "PhiStart:=", "0deg",
        "PhiStop:=", "360deg",
        "PhiStep:=", "5deg"
    ]
)

# ---------- Far-Field Report (3D Polar) ----------
oModuleRpt = oDesign.GetModule("ReportSetup")
oModuleRpt.CreateReport(
    "Gain3D_Total",
    "Far Fields",
    "3D Polar Plot",
    "Setup1 : LastAdaptive",
    [
        "Context:=", "InfSphere1",
        "PolarPlotType:=", "3D"
    ],
    [
        "Theta:=", ["All"],
        "Phi:=",   ["All"]
    ],
    [
        "GainTotal"
    ],
    []
)

# ---------- Optimetrics: Param Sweeps for Sliders & Animation ----------
oOptimetrics = oDesign.GetModule("Optimetrics")

# Helper to safely insert parametric setup with LIST data (robust across versions)
def insert_parametric_setup(name, var_data_pairs, setupsel="Setup1", sweepname="Sweep1"):
    # var_data_pairs = [("h_lam","LIST(0.01,0.05,0.10,0.15,0.20,0.25)"), ...]
    vars_block = ["NAME:Variables"]
    for v, data in var_data_pairs:
        vars_block.append(
            [
                "NAME:Variable",
                "Variable:=", v,
                "Data:=", data,
                "OffsetF1:=", False,
                "Synchronize:=", 0
            ]
        )

    oOptimetrics.InsertSetup(
        "Parametric",
        [
            "NAME:" + name,
            "IsEnabled:=", True,
            [
                "NAME:ProdOptiSetupDataV2",
                "SaveFields:=", False,
                "CopyMesh:=", True
            ],
            [
                "NAME:StartingPoint"
            ],
            vars_block,
            [
                "NAME:Sweeps",
                [
                    "NAME:SweepDefinition",
                    "Variable:=", "Freq",
                    "Data:=", "All",  # use all points from the linked sweep or LastAdaptive
                    "OffsetF1:=", False
                ]
            ],
            "Setup:=", setupsel,
            "Sweep:=", sweepname
        ]
    )

# Parameter ranges guided by your MATLAB examples:
#   h/λ in [0.01, 0.25]
#   εr_real in [5, 81], εr_imag in [0, ~sigma/(ωε0)] -> expose both; default imag=0
#   σ in [1e-3, 5] S/m
#   μr_real in [1, 600], μr_imag in [0, 200] (covers 600 - j*150 ferrite example)
insert_parametric_setup(
    "Param_h_lam",
    [
        ("h_lam",  "LIST(0.01,0.05,0.10,0.15,0.20,0.25)")
    ]
)

insert_parametric_setup(
    "Param_eps",
    [
        ("epsr_re","LIST(5,13,30,50,81)"),
        ("epsr_im","LIST(0,0.5,1,2,4)")
    ]
)

insert_parametric_setup(
    "Param_mu",
    [
        ("mur_re","LIST(1,10,100,300,600)"),
        ("mur_im","LIST(0,25,50,100,150,200)")
    ]
)

insert_parametric_setup(
    "Param_sigma",
    [
        ("sigma","LIST(0.001S_per_m,0.005S_per_m,0.05S_per_m,0.5S_per_m,5S_per_m)")
    ]
)

# ---------- (Optional) Kick off a single solve at nominal to build fields ----------
# You can comment these two lines out if you prefer to run manually.
oDesign.AnalyzeAll()

# Tip: To animate the "Gain3D_Total" report over a parameter,
# use AEDT GUI: right-click the report > Create Animation > Vary Parameter.
# Or script it (API differs across versions). This script ensures all parameters are
# true design variables with Optimetrics sweeps, which makes the GUI animation controls appear.

# ===================== End of Script =====================
