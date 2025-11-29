#
# def generate_and_optimize_feature(
#         feature_name: str,
#         requirements_doc: str,
#         iterations: int = 3
# ):
#     """
#     1. Generates the Feature Crew and the Evaluation Crew.
#     2. Runs an initial test.
#     3. (Optional) Enters an optimization loop to refine agents.yaml.
#     """
#
#     # 1. Instantiate the Builder (Meta-Crew)
#     builder = AmshaBuilderApp()
#
#     # 2. Generate the Code (The "Twins")
#     # This generates both the Feature Code and the Evaluation Code
#     print(f"🏗️ Generating 'Doer' and 'Judge' crews for: {feature_name}...")
#     paths = builder.generate_twins(
#         name=feature_name,
#         context=requirements_doc
#     )
#
#     print(f"✅ Code generated at: {paths['feature_path']} and {paths['eval_path']}")
#     print("⚠️  Action Required: Please review the Evaluation Logic in 'tasks.yaml' before proceeding.")
#
#     user_approval = input("Is the Evaluation logic correct? (y/n): ")
#     if user_approval.lower() != 'y':
#         return
#
#     # 3. The Optimization Loop
#     current_score = 0
#     history = []
#
#     for i in range(iterations):
#         print(f"🔄 Optimization Cycle {i + 1}/{iterations}")
#
#         # A. Run the Feature
#         feature_output = _run_crew_dynamically(paths['feature_path'])
#
#         # B. Run the Evaluator
#         eval_report = _run_crew_dynamically(paths['eval_path'], input_data=feature_output)
#         current_score = eval_report['overall_score']
#
#         print(f"   Score: {current_score}/10")
#         if current_score >= 9:
#             print("🚀 Target Quality Reached!")
#             break
#
#         # C. The Optimizer Agent (Refines YAML only)
#         # This agent reads the critique and rewrites the Feature's agents.yaml
#         builder.optimize_config(
#             config_path=f"{paths['feature_path']}/config/agents.yaml",
#             critique=eval_report['critique'],
#             documentation=requirements_doc
#         )
#
#
# def _run_crew_dynamically(path, input_data=None):
#     # Helper to load and run a crew class by path using Amsha logic
#     pass