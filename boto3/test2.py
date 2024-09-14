def is_valid_naptr_record(record):
    parts = record.split()
    if len(parts) != 6:
        return False
    order, preference, flags, service, regex, replacement = parts
    return (
        order.isdigit() and
        preference.isdigit() and
        flags in ['u', 's'] and
        service.startswith('E2U+') and
        replacement.startswith('sip:')
    )

# Example usage
print(is_valid_naptr_record('100 10 "u" "E2U+sip" "!^.*$!sip:info@example.com! .'))  # True
