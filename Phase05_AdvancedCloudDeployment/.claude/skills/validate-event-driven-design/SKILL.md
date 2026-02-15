---
name: validate-event-driven-design
description: Checks designs for consistency, handles edge cases (e.g., duplicate events, out-of-order delivery), and recommends retention policies and partitioning strategies. Use when validating event-driven architecture designs for Todo applications to ensure reliability, consistency, and performance.
---

# Validate Event-Driven Design

This skill helps validate event-driven architecture designs for Todo applications by checking for consistency, handling edge cases, and recommending best practices for reliability and performance.

## When to Use This Skill

Use this skill when:
- Reviewing event-driven architecture designs before implementation
- Validating Kafka topic configurations and consumer groups
- Checking for potential consistency issues in distributed systems
- Planning retention policies and resource allocation
- Identifying potential failure scenarios and mitigation strategies
- Ensuring design aligns with business requirements and SLAs

## Validation Checklist

### 1. Consistency Checks

**Event Schema Consistency:**
- All events of the same type follow identical schema structure
- Required fields are consistently present across all events
- Enum values are standardized and documented
- Field naming conventions are uniform

**Topic Naming Consistency:**
- Topic names follow standard naming conventions (e.g., domain.subdomain.events)
- No duplicate topics serve similar purposes
- Topic names clearly indicate their purpose and domain

**Event Naming Consistency:**
- Event names follow standard convention (e.g., domain.action.object)
- No conflicting event names across domains
- Names are descriptive and unambiguous

### 2. Edge Case Handling

**Duplicate Event Prevention:**
- Events have unique identifiers (eventId)
- Consumer services are idempotent
- Deduplication strategies are in place
- Sequence numbers or timestamps prevent replay

**Out-of-Order Delivery:**
- Events carry sufficient timestamp information
- Consumers can handle events arriving in different orders
- Event sourcing handles causality correctly
- Sequence numbers maintain order when required

**Event Loss Prevention:**
- Appropriate replication factors for Kafka topics
- Proper acknowledgment mechanisms
- Dead letter queue strategies
- Event persistence before processing

**Partial Failure Handling:**
- Transaction boundaries are clearly defined
- Compensating actions for failed operations
- Sagas for multi-step processes
- Circuit breakers for failed dependencies

### 3. Performance Considerations

**Partitioning Strategy:**
- Adequate partitioning for expected throughput
- Partition key selection for balanced load
- Order preservation within logical groups
- Scalability without compromising ordering

**Consumer Group Design:**
- Appropriate number of consumers per group
- Load balancing across consumer instances
- Offset management strategy
- Failover and rebalancing handling

**Topic Configuration:**
- Proper replication factor (minimum 3 for production)
- Appropriate retention policies (time and size)
- Log compaction settings where appropriate
- Partition size limits

### 4. Reliability Patterns

**Retry Mechanisms:**
- Exponential backoff for transient failures
- Maximum retry attempts defined
- Different retry strategies for different failure types
- Temporary vs permanent failure handling

**Circuit Breaker:**
- Circuit breaker patterns for downstream services
- Fallback mechanisms when circuit is open
- Automatic recovery and health checking
- Metrics collection during circuit states

**Timeout Handling:**
- Appropriate timeouts for external dependencies
- Graceful degradation when timeouts occur
- Correlation of timeout failures
- Retry vs failure distinction

## Design Review Process

### 1. Architecture Review
- Verify event-driven approach is appropriate for the use case
- Check for potential over-engineering
- Validate separation of concerns
- Ensure proper domain boundaries

### 2. Data Flow Analysis
- Trace complete event flows from source to destination
- Identify potential bottlenecks
- Verify data consistency requirements
- Check for circular dependencies

### 3. Error Path Analysis
- Map failure scenarios for each component
- Verify error handling at every step
- Check for proper monitoring and alerting
- Ensure graceful degradation

### 4. Scalability Assessment
- Estimate event volume and growth projections
- Validate partitioning strategy for scale
- Check resource utilization expectations
- Plan for traffic spikes

## Retention Policy Recommendations

### Topic-Level Retention
- Critical events: Permanent retention or long-term (years)
- Audit logs: Regulatory compliance period (months-years)
- Analytics data: Active period (weeks-months)
- Temporary events: Short-term (days-weeks)

### Compaction Strategies
- Use log compaction for entities that change frequently
- Key-based deduplication for entity state
- Balance between storage and performance
- Handle tombstone records appropriately

## Partitioning Strategy Guidelines

### High-Volume Topics
- Partition by user ID for user-specific events
- Partition by aggregate ID for entity events
- Consider geographic distribution for global systems
- Monitor partition balance and adjust as needed

### Ordering Requirements
- Maintain ordering within logical aggregates
- Allow parallel processing across different aggregates
- Use composite keys when multiple ordering dimensions exist
- Document ordering guarantees clearly

## Monitoring and Observability

### Key Metrics to Track
- Event production and consumption rates
- Consumer lag for each consumer group
- Error rates and retry counts
- End-to-end latency measurements

### Alerting Thresholds
- Consumer lag exceeding acceptable bounds
- Unexpected drop in event volume
- Increase in error rates
- Resource utilization approaching limits

## Validation Output Format

Provide validation results in the following format:

### Design Strengths
- [List positive aspects of the design]

### Identified Issues
- **Critical**: [Issues that could cause system failure]
- **High**: [Issues that impact reliability/consistency]
- **Medium**: [Issues affecting performance/efficiency]
- **Low**: [Minor improvements]

### Recommendations
- **Must Fix**: [Critical issues requiring immediate attention]
- **Should Fix**: [Important issues for improved design]
- **Could Fix**: [Optional improvements for consideration]

### Risk Assessment
- **High Risk**: [Areas with potential for significant problems]
- **Medium Risk**: [Areas needing monitoring]
- **Low Risk**: [Acceptable risk levels]

This comprehensive validation approach ensures event-driven designs are robust, scalable, and maintainable.