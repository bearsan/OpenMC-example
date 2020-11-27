import openmc
import numpy as np

# Material
fuel = openmc.Material(name='fuel')
fuel.set_density(units="atom/b-cm",density=8.0175E-2)
fuel.add_nuclide("U233",1.5621E-3,percent_type="ao")
fuel.add_nuclide("Th232",1.2639E-2,percent_type="ao")
fuel.add_nuclide("O16",2.8402E-2,percent_type="ao")
fuel.temperature = 1500

clad = openmc.Material(name='clad')
clad.set_density(units='atom/b-cm',density=4.3346E-2)
clad.add_nuclide("Zr91",1,percent_type="ao")
clad.temperature = 600

moderator = openmc.Material(name="moderator")
moderator.set_density(units="atom/b-cm",density=6.5491E-2)
moderator.add_nuclide("H2",4.3661E-2,percent_type="ao")
moderator.add_nuclide("O16",2.1830E-2,percent_type="ao")
moderator.temperature = 600
moderator.add_s_alpha_beta('c_D_in_D2O')

materials = openmc.Materials([fuel, clad, moderator])

# Geometry
fuel_r = [0.52273,0.57273]
cr_r = [0.5042,0.5461]
gt_r = [0.43688,0.48387,0.56134,0.60198]
pitch = 1.26
assembly_len = 21.42
axial_height = 200

# fuel pin
fuel_pin_surfaces = [openmc.ZCylinder(r=r) for r in fuel_r]
fuel_pin_univ = openmc.model.pin(fuel_pin_surfaces, openmc.Materials([fuel,clad,moderator]))

# control rod pin
cr_pin_surfaces = [openmc.ZCylinder(r=r) for r in cr_r]
cr_pin_univ = openmc.model.pin(cr_pin_surfaces, openmc.Materials([moderator,clad,moderator]))

# guide tube pin
gt_pin_surfaces = [openmc.ZCylinder(r=r) for r in gt_r]
gt_pin_univ = openmc.model.pin(gt_pin_surfaces, openmc.Materials([moderator,clad,moderator,clad,moderator]))

# assembly lattice
lattice = openmc.RectLattice()
lattice.lower_left = (-assembly_len/2, -assembly_len/2)
lattice.pitch = (pitch, pitch)
lat = np.tile(fuel_pin_univ, (17, 17))
# guide tube
lat[8,8] = gt_pin_univ
# control rod
lat[2,[5,8,11]]=cr_pin_univ
lat[14,[5,8,11]]=cr_pin_univ
lat[3,[3,13]]=cr_pin_univ
lat[13,[3,13]]=cr_pin_univ
lat[5,[2,5,8,11,14]]=cr_pin_univ
lat[11,[2,5,8,11,14]]=cr_pin_univ
lat[8,[2,5,11,14]]=cr_pin_univ

lattice.universes = lat

root_cell = openmc.Cell(name='root cell')
root_cell.fill = lattice
assembly_top = openmc.ZPlane(z0 = axial_height/2,boundary_type='reflective')
assembly_bottom = openmc.ZPlane(z0 = -axial_height/2,boundary_type='reflective')
bound_box = openmc.rectangular_prism(assembly_len, assembly_len, boundary_type="reflective")
root_cell.region = bound_box
root_cell.region = root_cell.region & -assembly_top & +assembly_bottom

root_univ = openmc.Universe(cells=[root_cell])
geometry = openmc.Geometry(root_univ)

# settings
settings = openmc.Settings()
settings.particles = 10000
settings.inactive = 100
settings.batches = 200
settings.temperature['multipole']= True
settings.temperature['method']= 'interpolation'

# plot
plot_xy = openmc.Plot(plot_id=1)
plot_xy.basis = 'xy'
plot_xy.filename = 'materials-xy-Height'
plot_xy.origin = [0, 0,0]
plot_xy.pixels = [3000, 3000]
plot_xy.width = (25, 25)
plot_xy.color_by = 'material'

plot_xz = openmc.Plot(plot_id=2)
plot_xz.basis = 'xz'
plot_xz.filename = 'materials-yz-Height'
plot_xz.origin = [0, 0,0]
plot_xz.pixels = [3000, 3000]
plot_xz.width = (100, 100)
plot_xz.color_by = 'material'

geometry.export_to_xml()
settings.export_to_xml()
materials.export_to_xml()
plot_file = openmc.Plots([plot_xy,plot_xz])
plot_file.export_to_xml()

# openmc.plot_geometry(output=False)
openmc.run()