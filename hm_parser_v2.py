#!/usr/bin/env python3
"""
HyperMesh .hm Binary File Parser (Improved)
=============================================
Attempts to extract geometry and mesh data from Altair HyperMesh .hm files.

The .hm format is a proprietary binary format. This parser uses pattern
recognition and heuristic analysis to extract node coordinates, element
connectivity, and other model information.

Usage:
    python hm_parser_v2.py <input.hm> [--output-dir <dir>]
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
    elem_type: str
    nodes: List[int] = field(default_factory=list)


@dataclass
class Component:
    """Represents a component/collector."""

    id: int
    name: str
    color: int = 0


@dataclass
class HMModel:
    """Container for all extracted HyperMesh model data."""

    nodes: Dict[int, Node] = field(default_factory=dict)
    elements: Dict[int, Element] = field(default_factory=dict)
    components: Dict[int, Component] = field(default_factory=dict)
    metadata: Dict[str, any] = field(default_factory=dict)


class HMParserV2:
    """Improved parser for Altair HyperMesh .hm binary files."""

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.data = None
        self.model = HMModel()

    def read_file(self) -> bytes:
        """Read and decompress the .hm file."""
        with open(self.filepath, "rb") as f:
            raw = f.read()

        gz_start = raw.find(b"\x1f\x8b\x08")
        if gz_start >= 0:
            self.data = gzip.decompress(raw[gz_start:])
        else:
            self.data = raw

        self.model.metadata["file_size_compressed"] = len(raw)
        self.model.metadata["file_size_decompressed"] = len(self.data)
        return self.data

    def _is_valid_coordinate(self, val: float) -> bool:
        """Check if a value looks like a valid coordinate."""
        if np.isnan(val) or np.isinf(val):
            return False
        # Coordinates should be reasonable (not extremely small or large)
        if abs(val) < 1e-10 or abs(val) > 1e10:
            return False
        return True

    def _is_valid_node_id(self, node_id: int) -> bool:
        """Check if a value looks like a valid node ID."""
        return 1 <= node_id <= 10000000

    def _extract_nodes_improved(self):
        """Extract nodes using improved heuristics."""
        data = self.data
        nodes = {}

        # Strategy: Look for patterns where we have node IDs followed by
        # three reasonable coordinate values
        # Pattern: [node_id (4 bytes)] [x (8 bytes)] [y (8 bytes)] [z (8 bytes)]

        for i in range(0, len(data) - 28, 4):
            try:
                # Read node ID as 4-byte integer
                node_id = struct.unpack("<I", data[i : i + 4])[0]

                if not self._is_valid_node_id(node_id):
                    continue

                # Read coordinates as 8-byte doubles
                x = struct.unpack("<d", data[i + 4 : i + 12])[0]
                y = struct.unpack("<d", data[i + 12 : i + 20])[0]
                z = struct.unpack("<d", data[i + 20 : i + 28])[0]

                # Validate coordinates
                if (
                    self._is_valid_coordinate(x)
                    and self._is_valid_coordinate(y)
                    and self._is_valid_coordinate(z)
                ):
                    # Additional check: coordinates shouldn't be all identical
                    if not (x == y == z):
                        if node_id not in nodes:
                            nodes[node_id] = Node(node_id, x, y, z)

            except:
                pass

        # If we didn't find enough nodes, try alternative pattern
        if len(nodes) < 100:
            nodes2 = {}
            # Try: [x (8)] [y (8)] [z (8)] pattern without explicit ID
            seq_id = 1
            for i in range(0, len(data) - 24, 8):
                try:
                    x = struct.unpack("<d", data[i : i + 8])[0]
                    y = struct.unpack("<d", data[i + 8 : i + 16])[0]
                    z = struct.unpack("<d", data[i + 16 : i + 24])[0]

                    if (
                        self._is_valid_coordinate(x)
                        and self._is_valid_coordinate(y)
                        and self._is_valid_coordinate(z)
                        and not (x == y == z)
                    ):
                        # Check if these look like real coordinates (not near zero)
                        if abs(x) > 0.01 or abs(y) > 0.01 or abs(z) > 0.01:
                            nodes2[seq_id] = Node(seq_id, x, y, z)
                            seq_id += 1
                except:
                    pass

            if len(nodes2) > len(nodes):
                nodes = nodes2

        # Try integer coordinates pattern
        if len(nodes) < 100:
            nodes3 = {}
            seq_id = 1
            for i in range(0, len(data) - 16, 4):
                try:
                    # Try 4 integers: [id] [x] [y] [z]
                    node_id = struct.unpack("<I", data[i : i + 4])[0]
                    x_int = struct.unpack("<i", data[i + 4 : i + 8])[0]
                    y_int = struct.unpack("<i", data[i + 8 : i + 12])[0]
                    z_int = struct.unpack("<i", data[i + 12 : i + 16])[0]

                    if (
                        self._is_valid_node_id(node_id)
                        and -100000 < x_int < 100000
                        and -100000 < y_int < 100000
                        and -100000 < z_int < 100000
                        and not (x_int == y_int == z_int == 0)
                    ):
                        if node_id not in nodes3:
                            nodes3[node_id] = Node(
                                node_id, float(x_int), float(y_int), float(z_int)
                            )
                except:
                    pass

            if len(nodes3) > len(nodes):
                nodes = nodes3

        self.model.nodes = nodes
        self.model.metadata["node_count"] = len(nodes)

    def _extract_elements_improved(self):
        """Extract elements using improved heuristics."""
        data = self.data
        elements = {}

        # Look for tetra element patterns (4 nodes per element)
        # Pattern: [n1] [n2] [n3] [n4] as consecutive integers

        elem_id = 1
        for i in range(0, len(data) - 16, 4):
            try:
                n1 = struct.unpack("<I", data[i : i + 4])[0]
                n2 = struct.unpack("<I", data[i + 4 : i + 8])[0]
                n3 = struct.unpack("<I", data[i + 8 : i + 12])[0]
                n4 = struct.unpack("<I", data[i + 12 : i + 16])[0]

                # Validate node IDs
                if (
                    self._is_valid_node_id(n1)
                    and self._is_valid_node_id(n2)
                    and self._is_valid_node_id(n3)
                    and self._is_valid_node_id(n4)
                ):
                    # Check if nodes are distinct
                    if len(set([n1, n2, n3, n4])) == 4:
                        # Check if node IDs are in a reasonable range
                        max_id = max(n1, n2, n3, n4)
                        min_id = min(n1, n2, n3, n4)

                        # Nodes should be relatively close in ID range
                        if max_id - min_id < 10000:
                            if elem_id not in elements:
                                elements[elem_id] = Element(
                                    id=elem_id,
                                    elem_type="tetra4",
                                    nodes=[n1, n2, n3, n4],
                                )
                                elem_id += 1

            except:
                pass

        # Also look for hex elements (8 nodes)
        hex_elem_id = len(elements) + 1
        for i in range(0, len(data) - 32, 4):
            try:
                nodes = []
                valid = True
                for j in range(8):
                    n = struct.unpack("<I", data[i + j * 4 : i + j * 4 + 4])[0]
                    if not self._is_valid_node_id(n):
                        valid = False
                        break
                    nodes.append(n)

                if valid and len(set(nodes)) == 8:
                    max_id = max(nodes)
                    min_id = min(nodes)
                    if max_id - min_id < 10000:
                        if hex_elem_id not in elements:
                            elements[hex_elem_id] = Element(
                                id=hex_elem_id, elem_type="hexa8", nodes=nodes
                            )
                            hex_elem_id += 1

            except:
                pass

        self.model.elements = elements
        self.model.metadata["element_count"] = len(elements)

    def parse(self) -> HMModel:
        """Parse the .hm file and extract model data."""
        if self.data is None:
            self.read_file()

        self._extract_nodes_improved()
        self._extract_elements_improved()

        return self.model

    def get_element_types_summary(self) -> Dict[str, int]:
        """Get summary of element types found."""
        summary = {}
        for elem in self.model.elements.values():
            summary[elem.elem_type] = summary.get(elem.elem_type, 0) + 1
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
    """Write mesh data in Abaqus INP format."""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("*HEADING\n")
        f.write("HyperMesh model exported to INP format\n")
        f.write(f"Nodes: {len(model.nodes)}, Elements: {len(model.elements)}\n")
        f.write("** Generated by hm_parser_v2.py\n")

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

        # Element sets
        for elem_type, elems in elem_by_type.items():
            f.write(f"*ELSET, ELSET=SET_{elem_type.upper()}\n")
            elem_ids = [str(e.id) for e in elems]
            for i in range(0, len(elem_ids), 16):
                f.write(", ".join(elem_ids[i : i + 16]) + "\n")


def write_step_geometry(model: HMModel, filepath: str):
    """Write geometry in STEP AP214 format."""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("ISO-10303-21;\n")
        f.write("HEADER;\n")
        f.write("FILE_DESCRIPTION(('HyperMesh Geometry Export'),'2;1');\n")
        f.write(
            "FILE_NAME('geometry.step','2026-01-01T00:00:00',('HyperMesh Export'),(''),'hm_parser_v2.py','HyperMesh','');\n"
        )
        f.write("FILE_SCHEMA(('AUTOMOTIVE_DESIGN')); \n")
        f.write("ENDSEC;\n\n")

        f.write("DATA;\n")
        entity_id = 1

        # Application context
        f.write(f"#{entity_id} = APPLICATION_CONTEXT('automotive_design');\n")
        app_ctx_id = entity_id
        entity_id += 1

        f.write(
            f"#{entity_id} = APPLICATION_PROTOCOL_DEFINITION('international standard','automotive_design',2000,#1);\n"
        )
        entity_id += 1

        # Units
        f.write(
            f"#{entity_id} = UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.E-06),#{entity_id + 1},'distance_accuracy_value','Maximum model space deviation');\n"
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

        f.write(
            f"#{entity_id} = (NAMED_UNIT(#{angle_unit_id}) NAMED_UNIT(#{solid_angle_unit_id})NAMED_UNIT(#{length_unit_id}) REPRESENTATION_CONTEXT(#1,'design') REPRESENTATION_CONTEXT(#1,'design') REPRESENTATION_CONTEXT(#1,'design'));\n"
        )
        global_units_id = entity_id
        entity_id += 1

        # Create points for nodes
        if model.nodes:
            point_ids = {}
            for node_id in sorted(model.nodes.keys())[:2000]:
                node = model.nodes[node_id]
                f.write(
                    f"#{entity_id} = CARTESIAN_POINT('',({node.x:.8e},{node.y:.8e},{node.z:.8e}));\n"
                )
                point_ids[node_id] = entity_id
                entity_id += 1

            # Vertex points
            vertex_ids = {}
            for node_id, point_id in point_ids.items():
                f.write(f"#{entity_id} = VERTEX_POINT('',#{point_id});\n")
                vertex_ids[node_id] = entity_id
                entity_id += 1

        f.write("ENDSEC;\n")
        f.write("END-ISO-10303-21;\n")


def write_technical_doc(model: HMModel, filepath: str, parser: HMParserV2):
    """Generate technical documentation."""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("=" * 72 + "\n")
        f.write("HyperMesh (.hm) File Technical Documentation\n")
        f.write("=" * 72 + "\n\n")

        f.write("1. FILE INFORMATION\n")
        f.write("-" * 40 + "\n")
        f.write(f"Source file: {parser.filepath}\n")
        f.write(
            f"Compressed size: {model.metadata.get('file_size_compressed', 'N/A')} bytes\n"
        )
        f.write(
            f"Decompressed size: {model.metadata.get('file_size_decompressed', 'N/A')} bytes\n"
        )
        f.write(
            f"Compression ratio: {model.metadata.get('file_size_compressed', 0) / max(model.metadata.get('file_size_decompressed', 1), 1):.2%}\n\n"
        )

        f.write("2. MODEL STATISTICS\n")
        f.write("-" * 40 + "\n")
        f.write(f"Total nodes: {len(model.nodes)}\n")
        f.write(f"Total elements: {len(model.elements)}\n")
        f.write(f"Components: {len(model.components)}\n\n")

        f.write("3. ELEMENT TYPE SUMMARY\n")
        f.write("-" * 40 + "\n")
        elem_summary = parser.get_element_types_summary()
        for elem_type, count in sorted(elem_summary.items()):
            f.write(f"  {elem_type}: {count}\n")
        f.write("\n")

        f.write("4. BOUNDING BOX\n")
        f.write("-" * 40 + "\n")
        bb_min, bb_max = parser.get_bounding_box()
        if model.nodes:
            f.write(f"  Min: ({bb_min[0]:.6f}, {bb_min[1]:.6f}, {bb_min[2]:.6f})\n")
            f.write(f"  Max: ({bb_max[0]:.6f}, {bb_max[1]:.6f}, {bb_max[2]:.6f})\n")
            f.write(
                f"  Size: ({bb_max[0] - bb_min[0]:.6f}, {bb_max[1] - bb_min[1]:.6f}, {bb_max[2] - bb_min[2]:.6f})\n\n"
            )

        f.write("5. SAMPLE NODES (first 30)\n")
        f.write("-" * 40 + "\n")
        f.write(f"{'ID':>10} {'X':>15} {'Y':>15} {'Z':>15}\n")
        for node_id in sorted(model.nodes.keys())[:30]:
            n = model.nodes[node_id]
            f.write(f"{n.id:>10} {n.x:>15.6f} {n.y:>15.6f} {n.z:>15.6f}\n")
        f.write("\n")

        f.write("6. SAMPLE ELEMENTS (first 30)\n")
        f.write("-" * 40 + "\n")
        for elem_id in sorted(model.elements.keys())[:30]:
            e = model.elements[elem_id]
            nodes_str = ", ".join(str(n) for n in e.nodes)
            f.write(f"  Element {e.id}: type={e.elem_type}, nodes=[{nodes_str}]\n")
        f.write("\n")

        f.write("7. BINARY FORMAT ANALYSIS\n")
        f.write("-" * 40 + "\n")
        f.write("The .hm format is a proprietary binary format developed by Altair\n")
        f.write("Engineering. Key observations:\n\n")
        f.write("  - File uses gzip compression\n")
        f.write("  - Binary data contains mixed integer and floating-point arrays\n")
        f.write("  - No public specification or open-source parser available\n")
        f.write("  - Format may vary between HyperMesh versions\n\n")

        f.write("8. PARSING LIMITATIONS\n")
        f.write("-" * 40 + "\n")
        f.write("This parser uses heuristic pattern matching which may:\n")
        f.write("  - Miss nodes/elements that don't match expected patterns\n")
        f.write("  - Extract false positives from binary data\n")
        f.write("  - Not preserve original element IDs or component assignments\n")
        f.write("  - Not extract all geometry information\n\n")
        f.write("For accurate parsing, use Altair HyperMesh or export to\n")
        f.write("standard formats (Nastran, Abaqus, IGES, STEP).\n\n")

        f.write("=" * 72 + "\n")
        f.write("End of Technical Documentation\n")
        f.write("=" * 72 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Parse Altair HyperMesh .hm files")
    parser.add_argument("input", help="Input .hm file path")
    parser.add_argument("--output-dir", default=".", help="Output directory")
    parser.add_argument("--verbose", "-v", action="store_true")

    args = parser.parse_args()

    print(f"Parsing: {args.input}")
    hm_parser = HMParserV2(args.input)
    model = hm_parser.parse()

    print(f"Extracted {len(model.nodes)} nodes, {len(model.elements)} elements")

    os.makedirs(args.output_dir, exist_ok=True)

    # Write outputs
    inp_path = os.path.join(args.output_dir, "mesh.inp")
    write_inp(model, inp_path)
    print(f"Mesh written to: {inp_path}")

    step_path = os.path.join(args.output_dir, "geometry.step")
    write_step_geometry(model, step_path)
    print(f"Geometry written to: {step_path}")

    doc_path = os.path.join(args.output_dir, "technical_doc.txt")
    write_technical_doc(model, doc_path, hm_parser)
    print(f"Documentation written to: {doc_path}")

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
