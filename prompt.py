def format_prompts_as_string(data_list):
    prompts = ""
    for item in data_list:
        prompt = f"\n**Question:** {item['question']}\n**Answer:** {item['answer']}\n**Reference Links:** {item['links']}\n"
        prompts += prompt

    return prompts


def fill_company_details(company_name, website, location, industry):
    details_template = f'''
**Company Details:**
- **Company Name:** {company_name}
- **Website:** {website}
- **Location:** {location}
- **Industry:** {industry}
'''
    return details_template


