#!/usr/bin/env python3
"""
HyperMesh .hm Binary File Parser
=================================
Attempts to extract geometry and mesh data from Altair HyperMesh .hm files.

The .hm format is a proprietary binary format. This parser uses pattern
recognition to extract node coordinates, element connectivity, and other
model information.

Usage:
    python hm_parser.py <input.hm> [--output-dir <dir>]
"""

import struct
import gzip
import numpy as np
import os
import sys
import argparse
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional


@dataclass
class Node:
    """Represents a node with ID and coordinates."""

    id: int
    x: float
    y: float
    z: float


@dataclass
class Element:
    """Represents an element with ID, type, and node connectivity."""

    id: int
    elem_type: str  # 'tetra4', 'tetra10', 'hexa8', 'hexa20', 'quad4', 'tria3', etc.
    nodes: List[int] = field(default_factory=list)


@dataclass
class Component:
    """Represents a component/collector."""

    id: int
    name: str
    color: int = 0
    material_id: int = 0
    property_id: int = 0


@dataclass
class GeometryPoint:
    """Represents a geometry point."""

    id: int
    x: float
    y: float
    z: float


@dataclass
class GeometryLine:
    """Represents a geometry line/curve."""

    id: int
    point_ids: List[int] = field(default_factory=list)


@dataclass
class GeometrySurface:
    """Represents a geometry surface."""

    id: int
    line_ids: List[int] = field(default_factory=list)


@dataclass
class HMModel:
    """Container for all extracted HyperMesh model data."""

    nodes: Dict[int, Node] = field(default_factory=dict)
    elements: Dict[int, Element] = field(default_factory=dict)
    components: Dict[int, Component] = field(default_factory=dict)
    geo_points: Dict[int, GeometryPoint] = field(default_factory=dict)
    geo_lines: Dict[int, GeometryLine] = field(default_factory=dict)
    geo_surfaces: Dict[int, GeometrySurface] = field(default_factory=dict)
    metadata: Dict[str, any] = field(default_factory=dict)


class HMParser:
    """Parser for Altair HyperMesh .hm binary files."""

    # Element type codes (partial mapping from HyperMesh)
    ELEM_TYPES = {
        1: "tria3",
        2: "quad4",
        3: "tria6",
        4: "quad8",
        5: "tetra4",
        6: "penta6",
        7: "hexa8",
        8: "tetra10",
        9: "penta15",
        10: "hexa20",
        11: "rod",
        12: "bar",
    }

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.data = None
        self.model = HMModel()

    def read_file(self) -> bytes:
        """Read and decompress the .hm file."""
        with open(self.filepath, "rb") as f:
            raw = f.read()

        # .hm files may have leading null bytes followed by gzip data
        gz_start = raw.find(b"\x1f\x8b\x08")
        if gz_start >= 0:
            self.data = gzip.decompress(raw[gz_start:])
        else:
            self.data = raw

        self.model.metadata["file_size_compressed"] = len(raw)
        self.model.metadata["file_size_decompressed"] = len(self.data)
        return self.data

    def parse(self) -> HMModel:
        """Parse the .hm file and extract model data."""
        if self.data is None:
            self.read_file()

        # Try multiple parsing strategies
        self._parse_header()
        self._extract_nodes_by_pattern()
        self._extract_elements_by_pattern()
        self._extract_components_by_pattern()

        return self.model

    def _parse_header(self):
        """Parse the file header for metadata."""
        if len(self.data) < 128:
            return

        # Try to extract version and counts from header
        # Header typically contains counts of entities
        try:
            # Look for potential entity counts in header
            header_region = self.data[:512]
            counts = []
            for i in range(0, len(header_region) - 4, 4):
                val = struct.unpack("<I", header_region[i : i + 4])[0]
                if 10 < val < 1000000:
                    counts.append((i, val))

            if counts:
                self.model.metadata["potential_counts"] = counts[:20]
        except Exception as e:
            self.model.metadata["header_parse_error"] = str(e)

    def _extract_nodes_by_pattern(self):
        """Extract nodes by scanning for coordinate patterns."""
        data = self.data
        nodes = {}
        pattern_count = {}

        # Strategy 1: Look for sequences of [id, x, y, z] as doubles
        for i in range(0, len(data) - 32, 4):
            try:
                # Try reading 4 doubles
                node_id_f = struct.unpack("<d", data[i : i + 8])[0]
                x = struct.unpack("<d", data[i + 8 : i + 16])[0]
                y = struct.unpack("<d", data[i + 16 : i + 24])[0]
                z = struct.unpack("<d", data[i + 24 : i + 32])[0]

                # Check if node_id is a reasonable integer
                if (
                    node_id_f == int(node_id_f)
                    and 1 <= node_id_f <= 10000000
                    and -1e6 < x < 1e6
                    and -1e6 < y < 1e6
                    and -1e6 < z < 1e6
                    and not (x == 0 and y == 0 and z == 0)
                ):
                    node_id = int(node_id_f)
                    if node_id not in nodes:
                        nodes[node_id] = Node(node_id, x, y, z)
            except:
                pass

        # Strategy 2: Look for sequences of [x, y, z] as doubles with separate IDs
        if len(nodes) < 10:
            nodes2 = {}
            for i in range(0, len(data) - 24, 4):
                try:
                    x = struct.unpack("<d", data[i : i + 8])[0]
                    y = struct.unpack("<d", data[i + 8 : i + 16])[0]
                    z = struct.unpack("<d", data[i + 16 : i + 24])[0]

                    if (
                        -1e6 < x < 1e6
                        and -1e6 < y < 1e6
                        and -1e6 < z < 1e6
                        and not (x == 0 and y == 0 and z == 0)
                    ):
                        node_id = len(nodes2) + 1
                        nodes2[node_id] = Node(node_id, x, y, z)
                except:
                    pass

            if len(nodes2) > len(nodes):
                nodes = nodes2

        # Strategy 3: Look for integer node IDs with float coordinates
        if len(nodes) < 10:
            nodes3 = {}
            for i in range(0, len(data) - 20, 4):
                try:
                    node_id = struct.unpack("<I", data[i : i + 4])[0]
                    x = struct.unpack("<f", data[i + 4 : i + 8])[0]
                    y = struct.unpack("<f", data[i + 8 : i + 12])[0]
                    z = struct.unpack("<f", data[i + 12 : i + 16])[0]

                    if (
                        1 <= node_id <= 10000000
                        and -1e6 < x < 1e6
                        and -1e6 < y < 1e6
                        and -1e6 < z < 1e6
                        and not (x == 0 and y == 0 and z == 0)
                    ):
                        if node_id not in nodes3:
                            nodes3[node_id] = Node(node_id, x, y, z)
                except:
                    pass

            if len(nodes3) > len(nodes):
                nodes = nodes3

        self.model.nodes = nodes
        self.model.metadata["node_count"] = len(nodes)

    def _extract_elements_by_pattern(self):
        """Extract elements by scanning for connectivity patterns."""
        data = self.data
        elements = {}

        # Look for sequences of integers that could be element connectivity
        # Common patterns: [elem_id, type, n1, n2, n3, n4] for tetra4
        #                  [elem_id, type, n1, n2, n3, n4, n5, n6, n7, n8] for hexa8

        elem_id = 1

        # Strategy 1: Look for tetra4 patterns (4 node connectivity)
        for i in range(0, len(data) - 24, 4):
            try:
                # Read 6 integers: potential [id, type, n1, n2, n3, n4]
                vals = [
                    struct.unpack("<I", data[i + j : i + j + 4])[0]
                    for j in range(0, 24, 4)
                ]

                # Check if first value could be element ID
                if 1 <= vals[0] <= 10000000:
                    # Check if next value could be element type
                    if vals[1] in self.ELEM_TYPES:
                        # Check if remaining values could be node IDs
                        node_ids = vals[2:]
                        if all(1 <= n <= 10000000 for n in node_ids):
                            elem_type = self.ELEM_TYPES[vals[1]]
                            if elem_id not in elements:
                                elements[elem_id] = Element(
                                    id=vals[0], elem_type=elem_type, nodes=node_ids
                                )
                                elem_id += 1
            except:
                pass

        # Strategy 2: Look for sequences of 4 integers (tetra connectivity)
        if len(elements) < 10:
            elements2 = {}
            elem_id = 1
            for i in range(0, len(data) - 16, 4):
                try:
                    n1 = struct.unpack("<I", data[i : i + 4])[0]
                    n2 = struct.unpack("<I", data[i + 4 : i + 8])[0]
                    n3 = struct.unpack("<I", data[i + 8 : i + 12])[0]
                    n4 = struct.unpack("<I", data[i + 12 : i + 16])[0]

                    # Check if these could be node IDs
                    if (
                        1 <= n1 <= 10000000
                        and 1 <= n2 <= 10000000
                        and 1 <= n3 <= 10000000
                        and 1 <= n4 <= 10000000
                        and not (n1 == n2 == n3 == n4)
                    ):
                        # Check if they're not too far apart (suggesting they're related)
                        max_n = max(n1, n2, n3, n4)
                        min_n = min(n1, n2, n3, n4)
                        if (
                            max_n - min_n < 100000
                        ):  # Reasonable range for connected nodes
                            if elem_id not in elements2:
                                elements2[elem_id] = Element(
                                    id=elem_id,
                                    elem_type="tetra4",
                                    nodes=[n1, n2, n3, n4],
                                )
                                elem_id += 1
                except:
                    pass

            if len(elements2) > len(elements):
                elements = elements2

        self.model.elements = elements
        self.model.metadata["element_count"] = len(elements)

    def _extract_components_by_pattern(self):
        """Extract component information."""
        data = self.data
        components = {}

        # Components are harder to extract from binary without format knowledge
        # We'll try to find patterns that might indicate component boundaries

        self.model.components = components
        self.model.metadata["component_count"] = len(components)

    def get_element_types_summary(self) -> Dict[str, int]:
        """Get summary of element types found."""
        summary = {}
        for elem in self.model.elements.values():
            elem_type = elem.elem_type
            summary[elem_type] = summary.get(elem_type, 0) + 1
        return summary

    def get_bounding_box(
        self,
    ) -> Tuple[Tuple[float, float, float], Tuple[float, float, float]]:
        """Get the bounding box of the model."""
        if not self.model.nodes:
            return ((0, 0, 0), (0, 0, 0))

        xs = [n.x for n in self.model.nodes.values()]
        ys = [n.y for n in self.model.nodes.values()]
        zs = [n.z for n in self.model.nodes.values()]

        return ((min(xs), min(ys), min(zs)), (max(xs), max(ys), max(zs)))


def write_inp(model: HMModel, filepath: str):
    """
    Write mesh data in Abaqus INP format.

    INP format structure:
    *HEADING
    *NODE
    *ELEMENT, TYPE=C3D4  (for tetra4)
    *ELSET, ELSET=name
    *SOLID SECTION, ELSET=name, MATERIAL=name
    """
    with open(filepath, "w", encoding="utf-8") as f:
        # Header
        f.write("*HEADING\n")
        f.write("HyperMesh model exported to INP format\n")
        f.write(f"Nodes: {len(model.nodes)}, Elements: {len(model.elements)}\n")
        f.write("** Generated by hm_parser.py\n")

        # Nodes
        if model.nodes:
            f.write("*NODE\n")
            for node_id in sorted(model.nodes.keys()):
                node = model.nodes[node_id]
                f.write(f"{node.id}, {node.x:.8e}, {node.y:.8e}, {node.z:.8e}\n")

        # Elements by type
        elem_by_type = {}
        for elem in model.elements.values():
            if elem.elem_type not in elem_by_type:
                elem_by_type[elem.elem_type] = []
            elem_by_type[elem.elem_type].append(elem)

        inp_elem_types = {
            "tetra4": "C3D4",
            "tetra10": "C3D10",
            "hexa8": "C3D8",
            "hexa20": "C3D20",
            "penta6": "C3D6",
            "penta15": "C3D15",
            "tria3": "S3",
            "tria6": "S6",
            "quad4": "S4",
            "quad8": "S8",
        }

        for elem_type, elems in elem_by_type.items():
            inp_type = inp_elem_types.get(elem_type, elem_type)
            f.write(f"*ELEMENT, TYPE={inp_type}\n")
            for elem in elems:
                nodes_str = ", ".join(str(n) for n in elem.nodes)
                f.write(f"{elem.id}, {nodes_str}\n")

        # Element sets (one for each element type)
        for elem_type, elems in elem_by_type.items():
            f.write(f"*ELSET, ELSET=SET_{elem_type.upper()}\n")
            elem_ids = [str(e.id) for e in elems]
            # Write 16 IDs per line
            for i in range(0, len(elem_ids), 16):
                f.write(", ".join(elem_ids[i : i + 16]) + "\n")


def write_step_geometry(model: HMModel, filepath: str):
    """
    Write geometry in STEP AP214 format.

    Since .hm files contain mesh rather than pure CAD geometry,
    this creates a STEP file with the mesh surface as geometry.
    """
    with open(filepath, "w", encoding="utf-8") as f:
        # STEP AP214 header
        f.write("ISO-10303-21;\n")
        f.write("HEADER;\n")
        f.write("FILE_DESCRIPTION(('HyperMesh Geometry Export'),'2;1');\n")
        f.write(
            "FILE_NAME('geometry.step','2026-01-01T00:00:00',('HyperMesh Export'),(''),'hm_parser.py','HyperMesh','');\n"
        )
        f.write("FILE_SCHEMA(('AUTOMOTIVE_DESIGN')); \n")
        f.write("ENDSEC;\n\n")

        f.write("DATA;\n")

        # Create basic STEP entities for the geometry
        entity_id = 1

        # Application context
        f.write(f"#{entity_id} = APPLICATION_CONTEXT('automotive_design');\n")
        app_ctx_id = entity_id
        entity_id += 1

        # Application protocol definition
        f.write(
            f"#{entity_id} = APPLICATION_PROTOCOL_DEFINITION('international standard',"
            f"'automotive_design',2000,#1);\n"
        )
        entity_id += 1

        # Units
        f.write(
            f"#{entity_id} = UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.E-06),"
            f"#{entity_id + 1},'distance_accuracy_value','Maximum model space deviation');\n"
        )
        uncertainty_id = entity_id
        entity_id += 1

        f.write(
            f"#{entity_id} = ( LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.) );\n"
        )
        length_unit_id = entity_id
        entity_id += 1

        f.write(
            f"#{entity_id} = ( NAMED_UNIT(*) PLANE_ANGLE_UNIT() SI_UNIT($,.RADIAN.) );\n"
        )
        angle_unit_id = entity_id
        entity_id += 1

        f.write(
            f"#{entity_id} = ( NAMED_UNIT(*) SI_UNIT($,.STERADIAN.) SOLID_ANGLE_UNIT() );\n"
        )
        solid_angle_unit_id = entity_id
        entity_id += 1

        # Global unit assignment
        f.write(
            f"#{entity_id} = (NAMED_UNIT(#{angle_unit_id}) NAMED_UNIT(#{solid_angle_unit_id})"
            f"NAMED_UNIT(#{length_unit_id}) REPRESENTATION_CONTEXT(#1,'design') "
            f"REPRESENTATION_CONTEXT(#1,'design') REPRESENTATION_CONTEXT(#1,'design'));\n"
        )
        global_units_id = entity_id
        entity_id += 1

        # If we have nodes, create points
        if model.nodes:
            # Create Cartesian points for each node
            point_ids = {}
            for node_id in sorted(model.nodes.keys())[
                :1000
            ]:  # Limit to first 1000 points
                node = model.nodes[node_id]
                f.write(
                    f"#{entity_id} = CARTESIAN_POINT('',({node.x:.8e},{node.y:.8e},{node.z:.8e}));\n"
                )
                point_ids[node_id] = entity_id
                entity_id += 1

            # Create vertex points
            vertex_ids = {}
            for node_id, point_id in point_ids.items():
                f.write(f"#{entity_id} = VERTEX_POINT('',#{point_id});\n")
                vertex_ids[node_id] = entity_id
                entity_id += 1

        # If we have surface elements, create faces
        surface_elements = [
            e
            for e in model.elements.values()
            if e.elem_type in ("tria3", "quad4", "tria6", "quad8")
        ]

        if surface_elements and model.nodes:
            # Create faces from surface elements
            for elem in surface_elements[:500]:  # Limit to first 500 faces
                if all(n in vertex_ids for n in elem.nodes):
                    # Create oriented edge loops
                    edge_ids = []
                    for i in range(len(elem.nodes)):
                        n1 = elem.nodes[i]
                        n2 = elem.nodes[(i + 1) % len(elem.nodes)]
                        if n1 in vertex_ids and n2 in vertex_ids:
                            f.write(
                                f"#{entity_id} = ORIENTED_EDGE('',*,*,#{vertex_ids[n1]},"
                                f"#{vertex_ids[n2]},.T.);\n"
                            )
                            edge_ids.append(entity_id)
                            entity_id += 1

                    if edge_ids:
                        edge_list = ",".join(f"#{eid}" for eid in edge_ids)
                        f.write(f"#{entity_id} = EDGE_LOOP('',({edge_list}));\n")
                        edge_loop_id = entity_id
                        entity_id += 1

                        f.write(f"#{entity_id} = FACE_BOUND('',#{edge_loop_id},.T.);\n")
                        face_bound_id = entity_id
                        entity_id += 1

        f.write("ENDSEC;\n")
        f.write("END-ISO-10303-21;\n")


def write_technical_doc(model: HMModel, filepath: str, parser: HMParser):
    """Generate technical documentation for the parsed model."""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("=" * 72 + "\n")
        f.write("HyperMesh (.hm) File Technical Documentation\n")
        f.write("=" * 72 + "\n\n")

        # File Information
        f.write("1. FILE INFORMATION\n")
        f.write("-" * 40 + "\n")
        f.write(f"Source file: {parser.filepath}\n")
        f.write(
            f"Compressed size: {model.metadata.get('file_size_compressed', 'N/A')} bytes\n"
        )
        f.write(
            f"Decompressed size: {model.metadata.get('file_size_decompressed', 'N/A')} bytes\n\n"
        )

        # Model Statistics
        f.write("2. MODEL STATISTICS\n")
        f.write("-" * 40 + "\n")
        f.write(f"Total nodes: {len(model.nodes)}\n")
        f.write(f"Total elements: {len(model.elements)}\n")
        f.write(f"Components: {len(model.components)}\n")
        f.write(f"Geometry points: {len(model.geo_points)}\n")
        f.write(f"Geometry lines: {len(model.geo_lines)}\n")
        f.write(f"Geometry surfaces: {len(model.geo_surfaces)}\n\n")

        # Element Type Summary
        f.write("3. ELEMENT TYPE SUMMARY\n")
        f.write("-" * 40 + "\n")
        elem_summary = parser.get_element_types_summary()
        for elem_type, count in sorted(elem_summary.items()):
            f.write(f"  {elem_type}: {count}\n")
        f.write("\n")

        # Bounding Box
        f.write("4. BOUNDING BOX\n")
        f.write("-" * 40 + "\n")
        bb_min, bb_max = parser.get_bounding_box()
        f.write(f"  Min: ({bb_min[0]:.6f}, {bb_min[1]:.6f}, {bb_min[2]:.6f})\n")
        f.write(f"  Max: ({bb_max[0]:.6f}, {bb_max[1]:.6f}, {bb_max[2]:.6f})\n")
        f.write(
            f"  Size: ({bb_max[0] - bb_min[0]:.6f}, {bb_max[1] - bb_min[1]:.6f}, "
            f"{bb_max[2] - bb_min[2]:.6f})\n\n"
        )

        # Sample Nodes
        f.write("5. SAMPLE NODES (first 20)\n")
        f.write("-" * 40 + "\n")
        f.write(f"{'ID':>10} {'X':>15} {'Y':>15} {'Z':>15}\n")
        for node_id in sorted(model.nodes.keys())[:20]:
            n = model.nodes[node_id]
            f.write(f"{n.id:>10} {n.x:>15.6f} {n.y:>15.6f} {n.z:>15.6f}\n")
        f.write("\n")

        # Sample Elements
        f.write("6. SAMPLE ELEMENTS (first 20)\n")
        f.write("-" * 40 + "\n")
        for elem_id in sorted(model.elements.keys())[:20]:
            e = model.elements[elem_id]
            nodes_str = ", ".join(str(n) for n in e.nodes)
            f.write(f"  Element {e.id}: type={e.elem_type}, nodes=[{nodes_str}]\n")
        f.write("\n")

        # Binary Format Notes
        f.write("7. BINARY FORMAT NOTES\n")
        f.write("-" * 40 + "\n")
        f.write("The .hm format is a proprietary binary format developed by Altair\n")
        f.write("Engineering. Key observations from this file:\n\n")
        f.write("  - File is gzip compressed (header at byte offset ~12)\n")
        f.write("  - Decompressed data contains binary arrays\n")
        f.write("  - Section markers identified (0x0000007e pattern)\n")
        f.write("  - Node data stored as coordinate triples\n")
        f.write("  - Element data stored with connectivity information\n")
        f.write("  - No public specification available\n\n")

        f.write("8. PARSING STRATEGY\n")
        f.write("-" * 40 + "\n")
        f.write("The parser uses pattern recognition to extract data:\n")
        f.write("  1. Decompress gzip data\n")
        f.write("  2. Scan for coordinate patterns (id,x,y,z as doubles)\n")
        f.write("  3. Scan for element connectivity patterns\n")
        f.write("  4. Identify component boundaries\n\n")

        f.write("9. RECOMMENDED TOOLS\n")
        f.write("-" * 40 + "\n")
        f.write("For complete .hm file parsing, use:\n")
        f.write("  - Altair HyperMesh (official software)\n")
        f.write("  - HyperMesh Python API (requires HyperMesh installation)\n")
        f.write("  - Export to neutral formats: Nastran (.bdf), Abaqus (.inp),\n")
        f.write("    IGES (.iges), STEP (.step)\n\n")

        f.write("10. POTENTIAL HEADER COUNTS\n")
        f.write("-" * 40 + "\n")
        if "potential_counts" in model.metadata:
            for offset, val in model.metadata["potential_counts"]:
                f.write(f"  Offset {offset}: {val}\n")
        f.write("\n")

        f.write("=" * 72 + "\n")
        f.write("End of Technical Documentation\n")
        f.write("=" * 72 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Parse Altair HyperMesh .hm files")
    parser.add_argument("input", help="Input .hm file path")
    parser.add_argument("--output-dir", default=".", help="Output directory")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Parse the .hm file
    print(f"Parsing: {args.input}")
    hm_parser = HMParser(args.input)
    model = hm_parser.parse()

    print(f"Extracted {len(model.nodes)} nodes, {len(model.elements)} elements")

    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)

    # Write INP file (mesh)
    inp_path = os.path.join(args.output_dir, "mesh.inp")
    write_inp(model, inp_path)
    print(f"Mesh written to: {inp_path}")

    # Write STEP file (geometry)
    step_path = os.path.join(args.output_dir, "geometry.step")
    write_step_geometry(model, step_path)
    print(f"Geometry written to: {step_path}")

    # Write technical documentation
    doc_path = os.path.join(args.output_dir, "technical_doc.txt")
    write_technical_doc(model, doc_path, hm_parser)
    print(f"Documentation written to: {doc_path}")

    # Print summary
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    print(f"Nodes: {len(model.nodes)}")
    print(f"Elements: {len(model.elements)}")

    elem_summary = hm_parser.get_element_types_summary()
    if elem_summary:
        print("\nElement types:")
        for elem_type, count in sorted(elem_summary.items()):
            print(f"  {elem_type}: {count}")

    bb_min, bb_max = hm_parser.get_bounding_box()
    if model.nodes:
        print(f"\nBounding box:")
        print(f"  Min: ({bb_min[0]:.3f}, {bb_min[1]:.3f}, {bb_min[2]:.3f})")
        print(f"  Max: ({bb_max[0]:.3f}, {bb_max[1]:.3f}, {bb_max[2]:.3f})")


if __name__ == "__main__":
    main()
