/********************************************************************************
 *                                                                              *
 * This file is part of IfcOpenShell.                                           *
 *                                                                              *
 * IfcOpenShell is free software: you can redistribute it and/or modify         *
 * it under the terms of the Lesser GNU General Public License as published by  *
 * the Free Software Foundation, either version 3.0 of the License, or          *
 * (at your option) any later version.                                          *
 *                                                                              *
 * IfcOpenShell is distributed in the hope that it will be useful,              *
 * but WITHOUT ANY WARRANTY; without even the implied warranty of               *
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                 *
 * Lesser GNU General Public License for more details.                          *
 *                                                                              *
 * You should have received a copy of the Lesser GNU General Public License     *
 * along with this program. If not, see <http://www.gnu.org/licenses/>.         *
 *                                                                              *
 ********************************************************************************/

#ifndef IFCGEOMITERATORSETTINGS_H
#define IFCGEOMITERATORSETTINGS_H

#include <array>

#include "ifc_geom_api.h"
#include "../ifcparse/IfcException.h"
#include "../ifcparse/IfcBaseClass.h"

namespace IfcGeom
{
    class IFC_GEOM_API IteratorSettings
    {
    public:
        /// Enumeration of setting identifiers. These settings define the
        /// behaviour of various aspects of IfcOpenShell.
        enum Setting : uint64_t
        {
            /// Specifies whether vertices are welded, meaning that the coordinates
            /// vector will only contain unique xyz-triplets. This results in a 
            /// manifold mesh which is useful for modelling applications, but might 
            /// result in unwanted shading artifacts in rendering applications.
            WELD_VERTICES = 1,
            /// Specifies whether to apply the local placements of building elements
            /// directly to the coordinates of the representation mesh rather than
            /// to represent the local placement in the 4x3 matrix, which will in that
            /// case be the identity matrix.
            USE_WORLD_COORDS = 1 << 1,
            /// Internally IfcOpenShell measures everything in meters. This settings
            /// specifies whether to convert IfcGeomObjects back to the units in which
            /// the geometry in the IFC file is specified.
            CONVERT_BACK_UNITS = 1 << 2,
            /// Specifies whether to use the Open Cascade BREP format for representation
            /// items rather than to create triangle meshes. This is useful is IfcOpenShell
            /// is used as a library in an application that is also built on Open Cascade.
            USE_BREP_DATA = 1 << 3,
            /// Specifies whether to sew IfcConnectedFaceSets (open and closed shells) to
            /// TopoDS_Shells or whether to keep them as a loose collection of faces.
            SEW_SHELLS = 1 << 4,
            /// Disables the subtraction of IfcOpeningElement representations from
            /// the related building element representations.
            DISABLE_OPENING_SUBTRACTIONS = 1 << 5,
            /// Disables the triangulation of the topological representations. Useful if
            /// the client application understands Open Cascade's native format.
            DISABLE_TRIANGULATION = 1 << 6,
            /// Applies default materials to entity instances without a surface style.
            APPLY_DEFAULT_MATERIALS = 1 << 7,
            /// Specifies whether to include subtypes of IfcCurve.
            INCLUDE_CURVES = 1 << 8,
            /// Specifies whether to exclude subtypes of IfcSolidModel and IfcSurface.
            EXCLUDE_SOLIDS_AND_SURFACES = 1 << 9,
            /// Disables computation of normals. Saves time and file size and is useful
            /// in instances where you're going to recompute normals for the exported
            /// model in other modelling application in any case.
            NO_NORMALS = 1 << 10,
            /// Generates UVs by using simple box projection. Requires normals.
            /// Applicable for OBJ and DAE output.
            GENERATE_UVS = 1 << 11,
            /// Specifies whether to slice representations according to associated IfcLayerSets.
            APPLY_LAYERSETS = 1 << 12,
			/// Search for a parent of type IfcBuildingStorey for each representation
			SEARCH_FLOOR = 1 << 13,
			///
			SITE_LOCAL_PLACEMENT = 1 << 14,
			///
			BUILDING_LOCAL_PLACEMENT = 1 << 15,
			///
			VALIDATE_QUANTITIES = 1 << 16,
			/// Assigns the first layer material to the entire product
			LAYERSET_FIRST = 1 << 17,
			/// Adds arrow heads to edge segments to signify edge direction
			EDGE_ARROWS = 1 << 18,
			/// Disables the evaluation of IfcBooleanResult and simply returns FirstOperand
			DISABLE_BOOLEAN_RESULT = 1 << 19,
			// Disables wire intersection checks
			NO_WIRE_INTERSECTION_CHECK = 1 << 20,
			// Set wire intersection tolerance to 0
			NO_WIRE_INTERSECTION_TOLERANCE = 1 << 21,
			// Sets kernel precision factor to 1
			STRICT_TOLERANCE = 1 << 22,
			/// Number of different setting flags.
			NUM_SETTINGS = 23,
        };

        IteratorSettings()
            : settings_(WELD_VERTICES) // OR options that default to true here
            , deflection_tolerance_(1.e-3)
			, angular_tolerance_(0.5)
        {
        }

        /// Note that this is independent of the IFC length unit, one millimeter by default.
        double deflection_tolerance() const { return deflection_tolerance_; }
		double angular_tolerance() const { return angular_tolerance_; }
		double force_space_transparency() const { return force_space_transparency_; }
		std::set<int> context_ids() const { return context_ids_; }

        void set_deflection_tolerance(double value)
        {
            /// @todo Using deflection tolerance of 1e-6 or smaller hangs the conversion, research more in-depth.
            /// This bug can be reproduced e.g. with the Duplex model that can be found from http://www.nibs.org/?page=bsa_commonbimfiles#project1
            deflection_tolerance_ = value;
            if (deflection_tolerance_ <= 1e-6) {
                Logger::Message(Logger::LOG_WARNING, "Deflection tolerance cannot be set to <= 1e-6; using the default value 1e-3");
                deflection_tolerance_ = 1e-3;
            }
        }

		void set_angular_tolerance(double value) {
			angular_tolerance_ = value;
		}

		void force_space_transparency(double value) {
			force_space_transparency_ = value;
		}

		void set_context_ids(std::vector<int> value) {
			context_ids_ = std::set<int>(value.begin(), value.end());
		}

        /// Get boolean value for a single settings or for a combination of settings.
        bool get(unsigned setting) const
        {
            /// @todo If unknown setting value/combination: throw IfcParse::IfcException("Invalid IteratorSetting")?
            return (settings_ & setting) != 0;
        }

        /// Set boolean value for a single settings or for a combination of settings.
        void set(unsigned setting, bool value)
        {
            /// @todo If unknown setting value/combination: throw IfcParse::IfcException("Invalid IteratorSetting")?
            if (value) {
                settings_ |= setting;
            } else {
                settings_ &= ~setting;
            }
        }

        /// Optional offset that is applied to serialized objects, (0,0,0) by default.
        std::array<double,3> offset = std::array<double,3>{0.0, 0.0, 0.0};
        /// Optional rotation that is applied to serialized objects, (0,0,0,1) by default.
        std::array<double,4> rotation = std::array<double,4>{0.0, 0.0, 0.0, 1.0};

    protected:
		unsigned settings_;
        double deflection_tolerance_, angular_tolerance_, force_space_transparency_;
		std::set<int> context_ids_;
    };

    class IFC_GEOM_API ElementSettings : public IteratorSettings
    {
    public:
        ElementSettings(const IteratorSettings& settings,
            double unit_magnitude,
            const std::string& element_type)
            : IteratorSettings(settings)
            , unit_magnitude_(unit_magnitude)
            , element_type_(element_type)
        {
        }

        double unit_magnitude() const { return unit_magnitude_; }
        const std::string& element_type() const { return element_type_; }

    private:
        double unit_magnitude_;
        std::string element_type_;
    };
}

#endif
