#include <pybind11/pybind11.h>
#include <pybind11/stl.h> // CRITICAL: Allows Python lists to auto-convert to C++ std::vector
#include "steel_database.hpp"
#include "bom_calculator.hpp" 

namespace py = pybind11;

PYBIND11_MODULE(bom_core, m) {
    m.doc() = "C++ Backend for Enterprise BOM Steel Calculations";

    py::class_<OrderItems>(m, "OrderItems")
        .def(py::init<>()) 
        .def(py::init<std::string, std::string, int, double, double>()) 
        .def_readwrite("drawing_name", &OrderItems::drawing_name)
        .def_readwrite("profile_name", &OrderItems::profile_name)
        .def_readwrite("quantity", &OrderItems::quantity)
        .def_readwrite("length_mm", &OrderItems::length_mm) 
        .def_readwrite("width_mm", &OrderItems::width_mm);  

    py::class_<DrawingItemResult>(m, "DrawingItemResult")
        .def(py::init<>())
        .def_readwrite("drawing_name", &DrawingItemResult::drawing_name)
        .def_readwrite("profile_name", &DrawingItemResult::profile_name)
        .def_readwrite("quantity", &DrawingItemResult::quantity)
        .def_readwrite("length_mm", &DrawingItemResult::length_mm)
        .def_readwrite("width_mm", &DrawingItemResult::width_mm)
        .def_readwrite("exact_weight_kg", &DrawingItemResult::exact_weight_kg)
        .def_readwrite("exact_total_length_or_area", &DrawingItemResult::exact_total_length_or_area)
        .def_readwrite("is_plate", &DrawingItemResult::is_plate);

    py::class_<SummaryItemResult>(m, "SummaryItemResult")
        .def(py::init<>())
        .def_readwrite("profile_name", &SummaryItemResult::profile_name)
        .def_readwrite("grand_total_length_or_area", &SummaryItemResult::grand_total_length_or_area)
        .def_readwrite("unit_weight", &SummaryItemResult::unit_weight)
        .def_readwrite("standard_bars_to_order", &SummaryItemResult::standard_bars_to_order)
        .def_readwrite("commercial_weight_kg", &SummaryItemResult::commercial_weight_kg)
        .def_readwrite("tonnage_mt", &SummaryItemResult::tonnage_mt)
        .def_readwrite("is_plate", &SummaryItemResult::is_plate)
        .def_readwrite("recommended_plate_size", &SummaryItemResult::recommended_plate_size);

    py::class_<ProjectResult>(m, "ProjectResult")
        .def(py::init<>())
        .def_readwrite("drawing_items", &ProjectResult::drawing_items)
        .def_readwrite("summary_items", &ProjectResult::summary_items)
        .def_readwrite("grand_total_tonnage", &ProjectResult::grand_total_tonnage);

    py::class_<SteelDatabase>(m, "SteelDatabase")
        .def(py::init<>())
        .def("loadProfileFromCSV", &SteelDatabase::loadProfileFromCSV)
        .def("get_weight", &SteelDatabase::get_weight);

    py::class_<BOMCalculator>(m, "BOMCalculator")
        .def(py::init<const SteelDatabase&, double>(), py::arg("database"), py::arg("standard_length") = 12.0)
        .def("calculate_project", &BOMCalculator::calculate_project);
}