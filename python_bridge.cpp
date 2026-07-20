#include <pybind11/pybind11.h>
#include "steel_database.hpp"
#include "BOM_Calculator.hpp"

namespace py = pybind11;

PYBIND11_MODULE(bom_core, m) {
    m.doc() = "C++ Backend for BOM Steel Calculations";

    // Mapped to your struct OrderItems
    py::class_<OrderItems>(m, "OrderItems")
        .def(py::init<>()) 
        .def(py::init<std::string, int, double>()) 
        .def_readwrite("profile_name", &OrderItems::profile_name)
        .def_readwrite("quantity", &OrderItems::quantity)
        .def_readwrite("length_per_item_m", &OrderItems::length_per_item_m);

    // FIXED: Now mapping to ProcessedItems (plural)
    py::class_<ProcessedItems>(m, "ProcessedItems")
        .def(py::init<>())
        .def_readwrite("profile_name", &ProcessedItems::profile_name)
        .def_readwrite("base_weight_kg", &ProcessedItems::base_weight_kg)
        .def_readwrite("commercial_weight_kg", &ProcessedItems::commercial_weight_kg)
        .def_readwrite("standard_bars_to_order", &ProcessedItems::standard_bars_to_order);

    py::class_<SteelDatabase>(m, "SteelDatabase")
        .def(py::init<>())
        .def("loadProfileFromCSV", &SteelDatabase::loadProfileFromCSV)
        .def("get_weight", &SteelDatabase::get_weight);

    py::class_<BOMCalculator>(m, "BOMCalculator")
        .def(py::init<const SteelDatabase&, double>(), py::arg("database"), py::arg("standard_length") = 12.0)
        .def("calculate_item", &BOMCalculator::calculate_item);
}