# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.

from bpy.types import Panel
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.attribute.data import Data


def draw_ui(context, layout, obj_type):
    obj = context.active_object if obj_type == "Object" else context.active_object.active_material
    oprops = obj.BIMObjectProperties
    props = obj.BIMAttributeProperties
    if oprops.ifc_definition_id not in Data.products:
        Data.load(IfcStore.get_file(), oprops.ifc_definition_id)

    if props.is_editing_attributes:
        row = layout.row(align=True)
        op = row.operator("bim.edit_attributes", icon="CHECKMARK", text="Save Attributes")
        op.obj_type = obj_type
        op.obj = obj.name
        op = row.operator("bim.disable_editing_attributes", icon="CANCEL", text="")
        op.obj_type = obj_type
        op.obj = obj.name

        for attribute in Data.products[oprops.ifc_definition_id]:
            if attribute["type"] == "entity":
                continue
            row = layout.row(align=True)
            blender_attribute = props.attributes.get(attribute["name"])
            if attribute["type"] == "string" or attribute["type"] == "list":
                row.prop(blender_attribute, "string_value", text=attribute["name"])
            elif attribute["type"] == "integer":
                row.prop(blender_attribute, "int_value", text=attribute["name"])
            elif attribute["type"] == "float":
                row.prop(blender_attribute, "float_value", text=attribute["name"])
            elif attribute["type"] == "enum":
                row.prop(blender_attribute, "enum_value", text=attribute["name"])

            if attribute["name"] == "GlobalId":
                row.operator("bim.generate_global_id", icon="FILE_REFRESH", text="")
            if attribute["is_optional"]:
                row.prop(
                    blender_attribute,
                    "is_null",
                    icon="RADIOBUT_OFF" if blender_attribute.is_null else "RADIOBUT_ON",
                    text="",
                )
    else:
        row = layout.row()
        op = row.operator("bim.enable_editing_attributes", icon="GREASEPENCIL", text="Edit")
        op.obj_type = obj_type
        op.obj = obj.name

        if "GlobalId" not in [a["name"] for a in Data.products[oprops.ifc_definition_id]]:
            row = layout.row(align=True)
            row.label(text="STEP ID")
            row.label(text=str(oprops.ifc_definition_id))

        for attribute in Data.products[oprops.ifc_definition_id]:
            if attribute["value"] is None or attribute["type"] == "entity":
                continue
            row = layout.row(align=True)
            row.label(text=attribute["name"])
            row.label(text=str(attribute["value"]))

    # TODO: reimplement, see #1222
    # if "IfcSite/" in context.active_object.name or "IfcBuilding/" in context.active_object.name:
    #    self.draw_addresses_ui()


class BIM_PT_object_attributes(Panel):
    bl_label = "IFC Attributes"
    bl_idname = "BIM_PT_object_attributes"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        if not context.active_object:
            return False
        if not IfcStore.get_element(context.active_object.BIMObjectProperties.ifc_definition_id):
            return False
        return bool(context.active_object.BIMObjectProperties.ifc_definition_id)

    def draw(self, context):
        draw_ui(context, self.layout, "Object")


class BIM_PT_material_attributes(Panel):
    bl_label = "IFC Material Attributes"
    bl_idname = "BIM_PT_material_attributes"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"

    @classmethod
    def poll(cls, context):
        if not IfcStore.get_file():
            return False
        try:
            return bool(context.active_object.active_material.BIMObjectProperties.ifc_definition_id)
        except:
            return False

    def draw(self, context):
        draw_ui(context, self.layout, "Material")
