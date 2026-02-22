#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <string>
#include <cmath>
#include <map>

namespace py = pybind11;

class FeatureExtractor {
public:
    FeatureExtractor() = default;

    // Calculates the Shannon entropy of a given string (URL)
    double calculate_entropy(const std::string& text) {
        std::map<char, int> frequencies;
        for (char c : text) {
            frequencies[c]++;
        }

        double entropy = 0.0;
        size_t length = text.length(); // FIXED: Changed int to size_t to prevent data loss warning
        for (auto const& [character, count] : frequencies) {
            double probability = static_cast<double>(count) / static_cast<double>(length);
            entropy -= probability * std::log2(probability);
        }
        return entropy;
    }

    // Extracts structural features from the URL
    std::map<std::string, double> extract_url_features(const std::string& url) {
        std::map<std::string, double> features;
        features["length"] = static_cast<double>(url.length());
        features["entropy"] = calculate_entropy(url);
        // TODO: Add robust parsing for subdomains, suspicious keywords, and TLD checks
        return features;
    }
};

// Pybind11 module definition
PYBIND11_MODULE(url_engine, m) {
    m.doc() = "High-performance C++ URL feature extraction module for OmniGuard.";
    
    py::class_<FeatureExtractor>(m, "FeatureExtractor")
        .def(py::init<>())
        .def("extract_url_features", &FeatureExtractor::extract_url_features, "Extracts statistical features from a URL.");
}