#!/usr/bin/env python3
"""
Spec Refinement Validation Script for Chat Features

This script provides automated validation for chat specifications
focusing on impact analysis, backward compatibility, feature completeness,
natural language coverage, bonus feature integration, and consistency verification.
"""

import re
import json
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ValidationResult:
    """Represents the result of a validation check"""
    name: str
    passed: bool
    details: str
    severity: str  # 'critical', 'high', 'medium', 'low'


class SpecRefinementValidator:
    """Main validator class for chat specifications"""

    def __init__(self):
        self.core_intents = [
            "add_task",
            "list_tasks",
            "complete_task",
            "update_task",
            "delete_task",
            "get_summary",
            "query_tasks"
        ]
        self.min_variations_per_intent = 15
        self.total_expected_examples = len(self.core_intents) * self.min_variations_per_intent

    def validate_impact_analysis(self, spec_content: str) -> List[ValidationResult]:
        """Validate that impact analysis is performed"""
        results = []

        # Check for performance impact analysis
        has_performance = bool(re.search(r'(performance|latency|response time|throughput)', spec_content, re.IGNORECASE))
        results.append(ValidationResult(
            name="Performance Impact Analysis",
            passed=has_performance,
            details="Specification should include performance impact analysis" if not has_performance else "Performance impact analysis found",
            severity="critical" if not has_performance else "low"
        ))

        # Check for security impact analysis
        has_security = bool(re.search(r'(security|vulnerability|privacy|compliance)', spec_content, re.IGNORECASE))
        results.append(ValidationResult(
            name="Security Impact Analysis",
            passed=has_security,
            details="Specification should include security impact analysis" if not has_security else "Security impact analysis found",
            severity="critical" if not has_security else "low"
        ))

        # Check for integration impact analysis
        has_integration = bool(re.search(r'(integration|dependency|compatibility|migration)', spec_content, re.IGNORECASE))
        results.append(ValidationResult(
            name="Integration Impact Analysis",
            passed=has_integration,
            details="Specification should include integration impact analysis" if not has_integration else "Integration impact analysis found",
            severity="high" if not has_integration else "low"
        ))

        return results

    def validate_backward_compatibility(self, spec_content: str) -> List[ValidationResult]:
        """Validate backward compatibility requirements"""
        results = []

        # Check for backward compatibility statement
        has_backward_compat = bool(re.search(r'(backward compatibility|compatibility|migration|upgrade|legacy)', spec_content, re.IGNORECASE))
        results.append(ValidationResult(
            name="Backward Compatibility Statement",
            passed=has_backward_compat,
            details="Specification should include backward compatibility considerations" if not has_backward_compat else "Backward compatibility considerations found",
            severity="critical" if not has_backward_compat else "low"
        ))

        # Check for API compatibility
        has_api_compat = bool(re.search(r'(API.*compatibility|endpoint.*existing|request.*format.*unchanged)', spec_content, re.IGNORECASE))
        results.append(ValidationResult(
            name="API Compatibility",
            passed=has_api_compat,
            details="Specification should address API compatibility" if not has_api_compat else "API compatibility addressed",
            severity="critical" if not has_api_compat else "low"
        ))

        # Check for data model compatibility
        has_data_compat = bool(re.search(r'(data.*model.*compatibility|schema.*evolution|migration.*strategy)', spec_content, re.IGNORECASE))
        results.append(ValidationResult(
            name="Data Model Compatibility",
            passed=has_data_compat,
            details="Specification should address data model compatibility" if not has_data_compat else "Data model compatibility addressed",
            severity="high" if not has_data_compat else "low"
        ))

        return results

    def validate_feature_completeness(self, spec_content: str) -> List[ValidationResult]:
        """Validate feature completeness"""
        results = []

        # Check for functional requirements
        has_functional = bool(re.search(r'(functional.*requirement|what.*should.*do|feature.*specification)', spec_content, re.IGNORECASE))
        results.append(ValidationResult(
            name="Functional Requirements",
            passed=has_functional,
            details="Specification should include functional requirements" if not has_functional else "Functional requirements found",
            severity="critical" if not has_functional else "low"
        ))

        # Check for non-functional requirements
        has_non_functional = bool(re.search(r'(performance|security|reliability|scalability|availability)', spec_content, re.IGNORECASE))
        results.append(ValidationResult(
            name="Non-functional Requirements",
            passed=has_non_functional,
            details="Specification should include non-functional requirements" if not has_non_functional else "Non-functional requirements found",
            severity="critical" if not has_non_functional else "low"
        ))

        # Check for error conditions
        has_error_handling = bool(re.search(r'(error|exception|failure|recovery|fallback)', spec_content, re.IGNORECASE))
        results.append(ValidationResult(
            name="Error Handling",
            passed=has_error_handling,
            details="Specification should include error handling requirements" if not has_error_handling else "Error handling requirements found",
            severity="critical" if not has_error_handling else "low"
        ))

        # Check for edge cases
        has_edge_cases = bool(re.search(r'(edge case|boundary condition|limit|constraint)', spec_content, re.IGNORECASE))
        results.append(ValidationResult(
            name="Edge Cases",
            passed=has_edge_cases,
            details="Specification should address edge cases" if not has_edge_cases else "Edge cases addressed",
            severity="high" if not has_edge_cases else "low"
        ))

        return results

    def analyze_natural_language_coverage(self, spec_content: str) -> List[ValidationResult]:
        """Analyze natural language coverage for all intents"""
        results = []

        # Count variations per intent - improved pattern matching
        intent_counts = {}
        for intent in self.core_intents:
            # Look for intent variations in the spec with more flexible matching
            # This pattern looks for intent names followed by examples in various formats
            patterns = [
                rf'#?\s*Intent:\s*{intent}\s*(?:-|\n|\r\n)(.*?)(?=#?\s*Intent:|$)',  # Matches intent sections
                rf'\b{intent}\b.*?(?:\n\s*-*\s*".*?"|\n\s*\d+\..*?|\n\s*-\s*.*?)(.*?)(?=\n\s*#\s*|\n\s*Intent:|$)',  # Matches intent with examples
            ]

            count = 0
            for pattern in patterns:
                matches = re.findall(pattern, spec_content, re.IGNORECASE | re.DOTALL)
                # Count actual examples within each match
                for match in matches:
                    # Count lines that look like examples (contain quotes, dashes, etc.)
                    example_lines = re.findall(r'(?:^|\n)\s*[-*]\s*[^\n]*', match)
                    count += len(example_lines)

            # If no structured examples found, try to find loose examples mentioning the intent
            if count == 0:
                loose_matches = re.findall(rf'{intent}[^\.!?]*?(?:\n|$)', spec_content, re.IGNORECASE)
                count = len(loose_matches)

            intent_counts[intent] = count

        # Validate minimum variations per intent
        for intent, count in intent_counts.items():
            passed = count >= self.min_variations_per_intent
            results.append(ValidationResult(
                name=f"Intent {intent} Coverage",
                passed=passed,
                details=f"Intent {intent} has {count} variations, needs at least {self.min_variations_per_intent}" if not passed else f"Intent {intent} has {count} variations (minimum met)",
                severity="critical" if not passed else "low"
            ))

        # Total coverage validation
        total_variations = sum(intent_counts.values())
        total_passed = total_variations >= self.total_expected_examples
        results.append(ValidationResult(
            name="Total Natural Language Coverage",
            passed=total_passed,
            details=f"Total variations: {total_variations}, needs at least {self.total_expected_examples}" if not total_passed else f"Total variations: {total_variations} (minimum met)",
            severity="critical" if not total_passed else "low"
        ))

        # Check for Urdu language support
        has_urdu = bool(re.search(r'[^\x00-\x7F]', spec_content))  # Check for non-ASCII characters
        results.append(ValidationResult(
            name="Urdu Language Support",
            passed=has_urdu,
            details="Specification should include Urdu language examples" if not has_urdu else "Urdu language examples found",
            severity="high" if not has_urdu else "low"  # High if this is a bonus feature requirement
        ))

        # Check for voice input patterns
        has_voice_patterns = bool(re.search(r'(voice|audio|speech|recognition|stt|tts)', spec_content, re.IGNORECASE))
        results.append(ValidationResult(
            name="Voice Input Patterns",
            passed=has_voice_patterns,
            details="Specification should include voice input patterns" if not has_voice_patterns else "Voice input patterns found",
            severity="high" if not has_voice_patterns else "low"  # High if this is a bonus feature requirement
        ))

        return results

    def validate_bonus_feature_integration(self, spec_content: str) -> List[ValidationResult]:
        """Validate bonus feature integration (Urdu, voice)"""
        results = []

        # Check for Urdu implementation details
        has_urdu_details = bool(re.search(r'(urdu.*implementation|unicode.*normalization|rtl.*rendering|naskh.*font)', spec_content, re.IGNORECASE))
        results.append(ValidationResult(
            name="Urdu Implementation Details",
            passed=has_urdu_details,
            details="Specification should include detailed Urdu implementation" if not has_urdu_details else "Urdu implementation details found",
            severity="high" if not has_urdu_details else "low"
        ))

        # Check for voice input implementation details
        has_voice_details = bool(re.search(r'(voice.*input.*implementation|stt.*service|audio.*processing|mediarecorder)', spec_content, re.IGNORECASE))
        results.append(ValidationResult(
            name="Voice Input Implementation Details",
            passed=has_voice_details,
            details="Specification should include detailed voice input implementation" if not has_voice_details else "Voice input implementation details found",
            severity="high" if not has_voice_details else "low"
        ))

        # Check for privacy compliance for bonus features
        has_privacy = bool(re.search(r'(privacy|compliance|gdpr|ccpa|audio.*data)', spec_content, re.IGNORECASE))
        results.append(ValidationResult(
            name="Privacy Compliance for Bonus Features",
            passed=has_privacy,
            details="Specification should address privacy compliance for bonus features" if not has_privacy else "Privacy compliance addressed",
            severity="critical" if not has_privacy else "low"
        ))

        return results

    def validate_consistency_verification(self, spec_content: str) -> List[ValidationResult]:
        """Validate consistency with existing patterns"""
        results = []

        # Check for naming convention consistency
        has_naming = bool(re.search(r'(naming.*convention|naming.*pattern|terminology)', spec_content, re.IGNORECASE))
        results.append(ValidationResult(
            name="Naming Convention Consistency",
            passed=has_naming,
            details="Specification should follow existing naming conventions" if not has_naming else "Naming convention consistency addressed",
            severity="medium" if not has_naming else "low"
        ))

        # Check for API structure consistency
        has_api_structure = bool(re.search(r'(api.*structure|endpoint.*pattern|response.*format)', spec_content, re.IGNORECASE))
        results.append(ValidationResult(
            name="API Structure Consistency",
            passed=has_api_structure,
            details="Specification should follow existing API structure patterns" if not has_api_structure else "API structure consistency addressed",
            severity="high" if not has_api_structure else "low"
        ))

        # Check for validation rule consistency
        has_validation = bool(re.search(r'(validation.*rule|validation.*pattern|constraint.*definition)', spec_content, re.IGNORECASE))
        results.append(ValidationResult(
            name="Validation Rule Consistency",
            passed=has_validation,
            details="Specification should follow existing validation patterns" if not has_validation else "Validation rule consistency addressed",
            severity="high" if not has_validation else "low"
        ))

        return results

    def validate_specification(self, spec_path: str) -> Dict[str, Any]:
        """Validate a complete specification file"""
        spec_file = Path(spec_path)
        if not spec_file.exists():
            raise FileNotFoundError(f"Specification file not found: {spec_path}")

        with open(spec_file, 'r', encoding='utf-8') as f:
            spec_content = f.read()

        # Run all validation checks
        results = {
            "impact_analysis": self.validate_impact_analysis(spec_content),
            "backward_compatibility": self.validate_backward_compatibility(spec_content),
            "feature_completeness": self.validate_feature_completeness(spec_content),
            "natural_language_coverage": self.analyze_natural_language_coverage(spec_content),
            "bonus_feature_integration": self.validate_bonus_feature_integration(spec_content),
            "consistency_verification": self.validate_consistency_verification(spec_content)
        }

        # Calculate overall summary
        all_results = []
        for category, category_results in results.items():
            all_results.extend(category_results)

        passed_count = sum(1 for r in all_results if r.passed)
        total_count = len(all_results)
        critical_failures = sum(1 for r in all_results if not r.passed and r.severity == "critical")

        summary = {
            "overall_score": f"{passed_count}/{total_count}",
            "passed_percentage": round((passed_count / total_count) * 100, 2),
            "critical_failures": critical_failures,
            "status": "PASS" if critical_failures == 0 and passed_count / total_count >= 0.8 else "FAIL"
        }

        return {
            "summary": summary,
            "detailed_results": results,
            "spec_path": spec_path
        }

    def generate_validation_report(self, validation_results: Dict[str, Any]) -> str:
        """Generate a human-readable validation report"""
        report = []
        report.append("# Specification Validation Report\n")
        report.append(f"## Summary")
        report.append(f"- Status: {validation_results['summary']['status']}")
        report.append(f"- Score: {validation_results['summary']['overall_score']} ({validation_results['summary']['passed_percentage']}%)")
        report.append(f"- Critical Failures: {validation_results['summary']['critical_failures']}")
        report.append(f"- Specification: {validation_results['spec_path']}")
        report.append("")

        # Detailed results by category
        for category, results in validation_results['detailed_results'].items():
            report.append(f"## {category.replace('_', ' ').title()}")
            for result in results:
                status = "✅" if result.passed else "❌"
                severity = f" [{result.severity.upper()}]" if not result.passed else ""
                report.append(f"{status} {result.name}{severity}")
                if not result.passed:
                    report.append(f"   - {result.details}")
            report.append("")

        return "\n".join(report)


def main():
    """Command line interface for the validator"""
    import argparse

    parser = argparse.ArgumentParser(description="Validate chat specifications using the Spec Refinement framework")
    parser.add_argument("spec_path", help="Path to the specification file to validate")
    parser.add_argument("--output", "-o", help="Output file for validation report (optional)")

    args = parser.parse_args()

    validator = SpecRefinementValidator()

    try:
        results = validator.validate_specification(args.spec_path)
        report = validator.generate_validation_report(results)

        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"Validation report saved to: {args.output}")
        else:
            print(report)

        # Exit with error code if validation failed
        if results['summary']['status'] == 'FAIL':
            exit(1)

    except Exception as e:
        print(f"Error validating specification: {str(e)}")
        exit(1)


if __name__ == "__main__":
    main()