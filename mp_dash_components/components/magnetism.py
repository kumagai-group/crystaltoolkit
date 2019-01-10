import dash_core_components as dcc
import dash_html_components as html

from dash.dependencies import Input, Output, State

from mp_dash_components.helpers.layouts import Columns, Column
from mp_dash_components.components.core import PanelComponent
from mp_dash_components.components.structure import StructureMoleculeComponent

from pymatgen.analysis.magnetism import CollinearMagneticStructureAnalyzer


class MagnetismComponent(PanelComponent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.viewer_component = StructureMoleculeComponent(
            id=self.id("structure"), color_scheme="magmom"
        )

    @property
    def all_layouts(self):
        all_layouts = super().all_layouts

        all_layouts["viewer"] = html.Div()#self.viewer_component.standard_layout

        return all_layouts

    @property
    def title(self):
        return "Magnetic Properties"

    @property
    def description(self):
        return (
            "Information on magnetic moments and magnetic "
            "ordering of this crystal structure."
        )

    @property
    def loading_text(self):
        return "Creating visualization of magnetic structure"

    def update_contents(self, new_store_contents):

        struct = self.from_data(new_store_contents)

        msa = CollinearMagneticStructureAnalyzer(struct, round_magmoms=1)
        if not msa.is_magnetic:
            # TODO: detect magnetic elements (?)
            return html.Div(
                "This structure is not magnetic or does not have "
                "magnetic information associated with it."
            )

        mag_species_and_magmoms = msa.magnetic_species_and_magmoms
        for k, v in mag_species_and_magmoms.items():
            if not isinstance(v, list):
                mag_species_and_magmoms[k] = [v]
        magnetic_atoms = "\n".join(
            [
                f"{sp} ({', '.join([f'{magmom} µB' for magmom in magmoms])})"
                for sp, magmoms in mag_species_and_magmoms.items()
            ]
        )

        magnetization_per_formula_unit = (
            msa.total_magmoms
            / msa.structure.composition.get_reduced_composition_and_factor()[1]
        )

        rows = []
        rows.append(
            (
                html.B("Total magnetization per formula unit"),
                html.Br(),
                f"{magnetization_per_formula_unit:.1f} µB",
            )
        )
        rows.append((html.B("Atoms with local magnetic moments"), html.Br(),
                     magnetic_atoms))

        data_block = html.Div([html.P([html.Span(cell) for cell in row]) for row in rows])

        return Columns([Column(self.viewer_layout), Column(data_block)])
