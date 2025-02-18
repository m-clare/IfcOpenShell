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

import bpy
import ifcopenshell.api
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.aggregate.data import Data


class AssignObject(bpy.types.Operator):
    bl_idname = "bim.assign_object"
    bl_label = "Assign Object"
    bl_options = {"REGISTER", "UNDO"}
    relating_object: bpy.props.StringProperty()
    related_object: bpy.props.StringProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        self.file = IfcStore.get_file()
        related_objects = (
            [bpy.data.objects.get(self.related_object)] if self.related_object else context.selected_objects
        )
        relating_object = bpy.data.objects.get(self.relating_object)
        if not relating_object or not relating_object.BIMObjectProperties.ifc_definition_id:
            return {"FINISHED"}
        for related_object in related_objects:
            oprops = related_object.BIMObjectProperties
            product = self.file.by_id(oprops.ifc_definition_id)
            ifcopenshell.api.run(
                "aggregate.assign_object",
                self.file,
                **{
                    "product": product,
                    "relating_object": self.file.by_id(relating_object.BIMObjectProperties.ifc_definition_id),
                },
            )
            bpy.ops.bim.edit_object_placement(obj=related_object.name)
            Data.load(IfcStore.get_file(), oprops.ifc_definition_id)
            bpy.ops.bim.disable_editing_aggregate(obj=related_object.name)

            spatial_collection = bpy.data.collections.get(related_object.name)
            relating_collection = bpy.data.collections.get(relating_object.name)
            if spatial_collection:
                self.remove_collection(context.scene.collection, spatial_collection)
                for collection in bpy.data.collections:
                    if collection == relating_collection:
                        if not collection.children.get(spatial_collection.name):
                            collection.children.link(spatial_collection)
                        continue
                    self.remove_collection(collection, spatial_collection)
            else:
                for collection in related_object.users_collection:
                    if collection.name.startswith("Ifc"):
                        collection.objects.unlink(related_object)
                relating_collection.objects.link(related_object)
        return {"FINISHED"}

    def remove_collection(self, parent, child):
        try:
            parent.children.unlink(child)
        except:
            pass


class EnableEditingAggregate(bpy.types.Operator):
    bl_idname = "bim.enable_editing_aggregate"
    bl_label = "Enable Editing Aggregate"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.active_object.BIMObjectProperties.relating_object = None
        context.active_object.BIMObjectProperties.is_editing_aggregate = True
        return {"FINISHED"}


class DisableEditingAggregate(bpy.types.Operator):
    bl_idname = "bim.disable_editing_aggregate"
    bl_label = "Disable Editing Aggregate"
    obj: bpy.props.StringProperty()
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else context.active_object
        obj.BIMObjectProperties.is_editing_aggregate = False
        return {"FINISHED"}


class AddAggregate(bpy.types.Operator):
    bl_idname = "bim.add_aggregate"
    bl_label = "Add Aggregate"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else context.active_object
        aggregate_collection = bpy.data.collections.new("IfcElementAssembly/Assembly")
        context.scene.collection.children.link(aggregate_collection)
        aggregate = bpy.data.objects.new("Assembly", None)
        aggregate_collection.objects.link(aggregate)
        bpy.ops.bim.assign_class(obj=aggregate.name, ifc_class="IfcElementAssembly")
        bpy.ops.bim.assign_object(related_object=obj.name, relating_object=aggregate.name)
        return {"FINISHED"}
