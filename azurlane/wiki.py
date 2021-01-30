import re

def get_template_value(src, key, default_value = None):
    existing_pattern = key + u'[ \t]*=[ \t]*(.*)'
    match = re.search(existing_pattern, src)
    if match:
        return match.group(1)
    else:
        return None
    
def set_template_value(src, key, new_value, insert_after_keys=[], insert_before_keys=[]):
    new_value = str(new_value)
    existing_pattern = key + u'[ \t]*=[ \t]*(.*)'
    match = re.search(existing_pattern, src)
    if match:
        if match.group(1) == new_value:
            return src
        else:
            existing_pattern = key + u'[ \t]*=[ \t]*(.*)'
            replacement = key + ' = ' + new_value
            return re.sub(existing_pattern, replacement, src, count=1)
    else:
        if isinstance(insert_before_keys, str): insert_before_keys = [insert_before_keys]
        for insert_before_key in insert_before_keys:
            insert_pattern = u'([ \t]*)\|([ \t]*)' + insert_before_key + u'[ \t]*=.*'
            match = re.search(insert_pattern, src)
            if match:
                indent_before_bar = match.group(1)
                indent_after_bar = match.group(2)
                return src[:match.start(0)]  + indent_before_bar + '|' + indent_after_bar + key + ' = ' + new_value + '\n' + src[match.start(0):]
        
        if isinstance(insert_after_keys, str): insert_after_keys = [insert_after_keys]
        for insert_after_key in insert_after_keys:
            insert_pattern = u'([ \t]*)\|([ \t]*)' + insert_after_key + u'[ \t]*=.*'
            match = re.search(insert_pattern, src)
            if match:
                indent_before_bar = match.group(1)
                indent_after_bar = match.group(2)
                return src[:match.end(0)] + '\n' + indent_before_bar + '|' + indent_after_bar + key + ' = ' + new_value + src[match.end(0):]
        raise Exception('Could not find any of the keys to insert after out of ' + str(insert_after_keys))
        

def set_template_values(src, items, insert_after_keys=[], insert_before_keys=[]):
    for key, value in items:
        src = set_template_value(src, key, value, insert_after_keys, insert_before_keys)
        insert_after_keys = [key]
        insert_before_keys = []
    return src

def delete_template_value(src, key):
    pattern = u'([ \t]*)\|([ \t]*)'  + key + u'[ \t]*=.*'
    return re.sub(pattern, '', src)

def map_page_titles(pages, key, value_type = None):
    def inner_iter():
        for page in pages:
            print(page.title)
            if '<tabber>' in page.text:
                for tab in page.text.split('|-|'):
                    # include newlines next to '='
                    tab_title_pattern = u'(.*)\s*=\s*\{\{'
                    match = re.search(tab_title_pattern, tab)
                    if match is None:
                        print(tab)
                    tab_title = match.group(1).strip()
                    yield page.title() + '#' + tab_title, tab
            else:
                yield page.title(), page.text
                
    result = {}
    
    for page_title, text in inner_iter():
        value = get_template_value(text, key)
        if value is None:
            print(text)
        if value_type is not None:
            value = value_type(value)
        result[value] = page_title
    
    return result
