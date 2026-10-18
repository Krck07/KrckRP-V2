# KoboldCpp Cheat Sheet

This document provides essential information for working with KoboldCpp's HTTP API, particularly for streaming responses and GBNF grammar constraint usage.

## Basic Endpoint Structure

```
POST /api/generate
Content-Type: application/json
Accept: text/event-stream  (for streaming)
```

## Standard Request Body Format

```json
{
  "prompt": "Your prompt here",
  "max_tokens": 200,
  "temperature": 0.7,
  "top_p": 0.9,
  "frequency_penalty": 0.5,
  "presence_penalty": 0.5,
  "stop": ["\n\n"],
  "stream": true
}
```

## Streaming Response Format

When `stream: true` is set, the endpoint returns Server-Sent Events (SSE) with this structure:

```text
data: {"token": "partial response text"}
```

For JSON-constrained output:
```text  
data: {"generated": "full valid JSON string"}
```

## Grammar Constraint Format (GBNF)

KoboldCpp uses GBNF (Generalized Backus-Naur Form) for grammar sampling. 

### Basic Structure
```gbnf
# Define a root rule that must match exactly one of the alternatives
root = "valid" | "alternatives"

# Define more complex structures with nested elements  
sentence = subject " " verb " " object
subject = "The cat" | "A dog"
verb = "runs" | "jumps"
object = "quickly" | "gracefully"
```

### JSON Schema Example
```gbnf
root = json_object

json_object = "{" ws (string ":" value ws ("," ws string ":" value)* )? "}"
value = string | number | boolean | null | json_object | json_array
number = "-"? ([0-9]+ "." [0-9]* | [0-9]+)
boolean = "true" | "false"
null = "null"
string = "\"" ([^"\r\n] | "\\\"" | "\\\\" | "\\n")* "\""
ws = [ \t\r\n]*
```

## Common Grammar Patterns for KrckRP

### Simple Schema Validation
```gbnf
root = action_proposal
action_proposal = "{" ws 
                    "\"action_type\": " string ws "," ws 
                    "\"target\": " string ws "," ws  
                    "\"result\": " string ws 
                  "}"
string = "\"" ([^"\r\n] | "\\\"" | "\\\\" | "\\n")* "\""
ws = [ \t\r\n]*
```

### Nested Object Validation
```gbnf
root = change_proposal
change_proposal = "{" ws
                    "\"character\": " string ws "," ws
                    "\"changes\": [" (change_item ("," ws change_item)*)? "]" ws 
                  "}"
change_item = "{" ws
                "\"field\": " string ws "," ws
                "\"old_value\": " value ws "," ws  
                "\"new_value\": " value ws
              "}"
value = string | number | boolean | null
string = "\"" ([^"\r\n] | "\\\"" | "\\\\" | "\\n")* "\""
number = "-"? [0-9]+ 
boolean = "true" | "false" 
null = "null"
ws = [ \t\r\n]*
```

## KoboldCpp Parameters for KrckRP

### For Narrator Model (Larger, more creative)
```json
{
  "prompt": "...",
  "max_tokens": 500,
  "temperature": 0.7,
  "top_p": 0.9,
  "frequency_penalty": 0.2,
  "presence_penalty": 0.1,
  "stream": true,
  "grammar": "your_gbnf_grammar_here"
}
```

### For Extractor Model (Smaller, precise JSON)
```json
{
  "prompt": "...",
  "max_tokens": 300,
  "temperature": 0.1,
  "top_p": 0.2,
  "frequency_penalty": 0.5,
  "presence_penalty": 0.5,
  "stream": true, 
  "grammar": "your_json_grammar_here"
}
```

## Usage Tips

1. **For JSON extraction**: Always provide a GBNF grammar that exactly matches your expected JSON structure
2. **Streaming vs Non-streaming**: Use streaming for better UX during generation; non-streaming when you need the full response at once  
3. **Temperature settings**:
   - High (0.7-1.0): More creative, varied output  
   - Low (0.1-0.4): More consistent, predictable
4. **Stop sequences**: Include appropriate stop tokens to prevent unwanted continuation

## Error Handling

KoboldCpp returns standard HTTP status codes:
- `200 OK`: Successful generation 
- `400 Bad Request`: Invalid parameters or grammar
- `500 Internal Server Error`: Model loading issues  

Response format for errors:
```json
{
  "error": "description of the error"
}
```