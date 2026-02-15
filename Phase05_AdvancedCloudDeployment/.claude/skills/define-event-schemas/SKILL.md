---
name: define-event-schemas
description: Produces detailed JSON Schema or Avro-compatible definitions for each event payload, including required fields (taskId, userId, title, priority, dueDate, recurrenceRule, status) and optional metadata. Use when defining event payload structures for Todo application events to ensure consistency and validation across services.
---

# Define Event Schemas

This skill helps create detailed JSON Schema or Avro-compatible definitions for Todo application event payloads, ensuring consistency and validation across services.

## When to Use This Skill

Use this skill when:
- Defining event payload structures for Todo application events
- Ensuring consistency across services that produce/consume events
- Setting up schema registry for Kafka events
- Validating event data in event-driven architectures
- Documenting API contracts for event schemas
- Generating code from schemas for type safety

## Schema Definition Process

### 1. Standard Event Schema Structure

All events should follow this standard structure:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "title": "Event Name",
  "description": "Description of the event",
  "properties": {
    "eventId": {
      "type": "string",
      "description": "Unique identifier for the event"
    },
    "eventType": {
      "type": "string",
      "description": "Type of the event"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 timestamp of when the event occurred"
    },
    "userId": {
      "type": "string",
      "description": "Identifier of the user who triggered the event"
    },
    "correlationId": {
      "type": "string",
      "description": "Request correlation identifier"
    },
    "data": {
      "type": "object",
      "description": "Event-specific data payload",
      "properties": {},
      "required": []
    },
    "metadata": {
      "type": "object",
      "description": "Additional metadata about the event",
      "properties": {
        "source": {
          "type": "string",
          "description": "Service that produced the event"
        },
        "version": {
          "type": "string",
          "description": "Schema version of the event"
        }
      }
    }
  },
  "required": ["eventId", "eventType", "timestamp", "userId", "data"]
}
```

### 2. Define Specific Event Schemas

For each specific event type, define the data properties:

#### Task Created Event
```json
{
  "type": "object",
  "title": "Task Created Event",
  "description": "Emitted when a new task is created",
  "properties": {
    "data": {
      "type": "object",
      "properties": {
        "taskId": { "type": "string" },
        "title": { "type": "string", "maxLength": 255 },
        "description": { "type": "string", "maxLength": 1000 },
        "priority": { "type": "string", "enum": ["low", "medium", "high", "urgent"] },
        "dueDate": { "type": "string", "format": "date-time" },
        "status": { "type": "string", "enum": ["pending", "in-progress", "completed", "cancelled"] },
        "tags": {
          "type": "array",
          "items": { "type": "string" }
        },
        "recurrenceRule": { "type": "string" }
      },
      "required": ["taskId", "title"]
    }
  }
}
```

#### Task Updated Event
```json
{
  "type": "object",
  "title": "Task Updated Event",
  "description": "Emitted when a task is updated",
  "properties": {
    "data": {
      "type": "object",
      "properties": {
        "taskId": { "type": "string" },
        "updates": {
          "type": "object",
          "description": "Map of updated fields",
          "properties": {
            "title": { "type": "string", "maxLength": 255 },
            "description": { "type": "string", "maxLength": 1000 },
            "priority": { "type": "string", "enum": ["low", "medium", "high", "urgent"] },
            "dueDate": { "type": "string", "format": "date-time" },
            "status": { "type": "string", "enum": ["pending", "in-progress", "completed", "cancelled"] },
            "tags": {
              "type": "array",
              "items": { "type": "string" }
            },
            "recurrenceRule": { "type": "string" }
          }
        },
        "previousValues": {
          "type": "object",
          "description": "Previous values of updated fields"
        }
      },
      "required": ["taskId", "updates"]
    }
  }
}
```

### 3. Common Field Definitions

Define reusable field definitions for consistency:

```json
{
  "definitions": {
    "taskId": {
      "type": "string",
      "pattern": "^[a-zA-Z0-9-_]+$",
      "maxLength": 50
    },
    "userId": {
      "type": "string",
      "pattern": "^[a-zA-Z0-9-_]+$",
      "maxLength": 50
    },
    "priority": {
      "type": "string",
      "enum": ["low", "medium", "high", "urgent"],
      "default": "medium"
    },
    "status": {
      "type": "string",
      "enum": ["pending", "in-progress", "completed", "cancelled"],
      "default": "pending"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time"
    },
    "tags": {
      "type": "array",
      "items": {
        "type": "string",
        "pattern": "^[a-zA-Z0-9_-]+$",
        "maxLength": 50
      },
      "maxItems": 10
    }
  }
}
```

### 4. Schema Versioning Strategy

Use semantic versioning for schema evolution:

- **Major version**: Breaking changes (removing fields, changing types)
- **Minor version**: Backward-compatible additions (adding optional fields)
- **Patch version**: Non-breaking fixes (clarifications, corrections)

Include version in the schema:

```json
{
  "metadata": {
    "version": "1.0.0",
    "compatibility": "backward" // forward, backward, full, none
  }
}
```

### 5. Validation Keywords

Use appropriate JSON Schema validation keywords:

- **Format validation**: `email`, `date-time`, `uri`
- **Pattern validation**: Regular expressions for custom formats
- **Range validation**: `minimum`, `maximum`, `minLength`, `maxLength`
- **Enum validation**: Fixed sets of allowed values
- **Conditional validation**: `if/then/else` for complex logic

## Avro Schema Compatibility

For Kafka integration, provide Avro-compatible schemas:

```json
{
  "type": "record",
  "name": "TaskCreatedEvent",
  "namespace": "com.todo.events",
  "fields": [
    {
      "name": "eventId",
      "type": "string"
    },
    {
      "name": "eventType",
      "type": "string",
      "default": "task.created"
    },
    {
      "name": "timestamp",
      "type": {
        "type": "long",
        "logicalType": "timestamp-micros"
      }
    },
    {
      "name": "userId",
      "type": "string"
    },
    {
      "name": "taskId",
      "type": "string"
    },
    {
      "name": "title",
      "type": "string"
    },
    {
      "name": "priority",
      "type": {
        "type": "enum",
        "name": "PriorityLevel",
        "symbols": ["LOW", "MEDIUM", "HIGH", "URGENT"]
      },
      "default": "MEDIUM"
    }
  ]
}
```

## Schema Registry Integration

Document schema registration requirements:

- Unique schema identifiers
- Version management
- Compatibility checks
- Consumer/producer validation

## Output Format

Generate schemas in the requested format (JSON Schema, Avro, or both) with:
- Complete field definitions
- Validation rules
- Examples
- Documentation comments
- Version information
- Compatibility guidelines