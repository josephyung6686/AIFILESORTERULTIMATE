#!/usr/bin/env swift
// Probe Apple Foundation Models availability (macOS / Apple Intelligence).
// Prints one line: available | unavailable | error:<msg>
import Foundation

#if canImport(FoundationModels)
import FoundationModels
@available(macOS 15.1, *)
func probe() {
    // LanguageModelSession exists when the framework is present; readiness
    // still depends on device Apple Intelligence entitlement.
    _ = SystemLanguageModel.self
    print("available")
}
if #available(macOS 15.1, *) {
    probe()
} else {
    print("unavailable")
}
#else
print("unavailable")
#endif
