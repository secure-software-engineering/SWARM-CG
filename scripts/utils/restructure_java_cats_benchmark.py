import os
import re

input_dir = 'jcg_testcases/src/main/resources'
output_dir = '../../benchmarks/java'

# Check or create output directory
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Parse markdown files and create new structure
def parse_and_create_structure(md_file):
    print(f"Processing file: {md_file}")
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract each testcase
    test_cases = re.findall(r'##\s*(.*?)\n(.*?)```java\n(.*?)\n```', content, re.DOTALL)
    print(f"Found {len(test_cases)} test cases in {md_file}")

    for test_case_name, description, java_code in test_cases:
        print(f"Found test case: {test_case_name}")

        # Clean test case name
        test_case_name = test_case_name.split('\n')[0].strip()
        test_case_name = re.sub(r'[^\w\s-]', '', test_case_name)
        test_case_name = re.sub(r'\s+', '_', test_case_name)

        # Directory structure
        md_file_name = os.path.basename(md_file)
        md_name = os.path.splitext(md_file_name)[0]
        test_case_dir = os.path.join(output_dir, md_name, test_case_name)
        os.makedirs(test_case_dir, exist_ok=True)

        # Java code to .java file
        java_file_path = os.path.join(test_case_dir, f'{test_case_name}.java')
        with open(java_file_path, 'w', encoding='utf-8') as java_file:
            java_file.write(java_code.strip() + '\n')
        print(f"Java file created: {java_file_path}")

        # Description to README.md file
        readme_file_path = os.path.join(test_case_dir, 'README.md')
        with open(readme_file_path, 'w', encoding='utf-8') as readme_file:
            readme_file.write(description.strip() + '\n')
        print(f"README file created: {readme_file_path}")

        # Empty callgraph.json file
        callgraph_file_path = os.path.join(test_case_dir, 'callgraph.json')
        open(callgraph_file_path, 'a').close()
        print(f"Callgraph file created: {callgraph_file_path}")

# Iterate through .md files
for root, dirs, files in os.walk(input_dir):
    for file in files:
        if file.endswith('.md'):
            md_file = os.path.join(root, file)
            parse_and_create_structure(md_file)

print("Microbenchmark restructured.")
