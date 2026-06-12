# Implementation Log

A. Summary
Prompt01 — Pipeline Repair and Full Validation Run.
G15B zero overlay bug was fixed in N4 side fields.
Track A and G21B got local full 2024 and frozen 2025 runs.
No official runtime promotion was done.

B. Files Created
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/logs/compileall_src_tests.log | created | command log
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/logs/full_pytest_tests.log | created | command log
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/logs/full_pytest_tests_nlpcc.log | created | command log
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/logs/git_diff_name_only_after.log | created | command log
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/logs/git_status_after.log | created | command log
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/logs/news_overlay_pytest.log | created | command log
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/logs/no_bytecode_compile_smoke.log | created | command log
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/logs/pip_check.log | created | command log
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/logs/prompt01_runner.log | created | command log
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/logs/python_version.log | created | command log
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/logs/rtk_version.log | created | command log
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/presented/agents_md_update_summary.md | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/presented/current_state_intake_summary.md | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/presented/final_candidate_decision_summary.md | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/presented/full_test_summary.md | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/presented/goal_a_track_a_overlay_repair_report.md | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/presented/goal_b_g15b_pipeline_repair_report.md | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/presented/goal_c_g21b_repaired_full_validation_report.md | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/presented/implementation_log.md | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/presented/output_package_status.md | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/presented/preflight_summary.md | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/progress/phase_folder_created.md | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/progress/runner_status.md | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/agent_guidance_files_audit.csv | created | audit table
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/agents_md_update_manifest.csv | created | audit table
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/011d80c3a1596ad4a58d5568d8e249f0f2106e7e053da1f1aec3fd21d689eb38.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/01aa312d8f10dc176c2b35deaad0a14be9a60540d765c742ee357ce8cd0e068a.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/01e67d7d0678c0e52a7602efa13ef3dbb780be9d8e41be7a5d836e887e0b83c3.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/02a2dcac6cbec97f8149724f4e5e9a6718b5c712965c956524883b0e7e0d621e.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/02a5956adbad6d9ec6c4bbd2b1199eff22c5026a7db06a49f51c5b3abc0f81d1.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/06cf161671196e92f9008ead47f634cc91c92e5041273ead937f3d0647797b6d.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/078984c77eec685d99c65e641c32e40c6550da60e673faba7d3631f5df1fa128.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/07a34a20617a4e9b79044c6f31a3b26930e1f2af6e6bb3da0951b41f5eb8f167.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/0904fcd9a817da718f67d22670d3a26df837a52acdd0c7e355c207301903b861.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/0937532c0cafbdc6b4f815f1a970408b09e1e4132a20da6022c3d9e550c48078.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/095ddbcc44a44233c5d80a59cfe34103451ee5ee8b3874c85837875a32084d72.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/0b3fa190b9b89ee19336866946c5a0c3ceb2af7ae725ee62f19e9b22b0b6c18b.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/0fb416721f2864344909504caf3b622aaa809a5415e890b099811f2007a8edb1.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/100c4eb450c4cc17eaf49f8262a42251f8aa5a0320b1899c1052cffe254112dc.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/10c5a0c8c2822bafce71e9cc14552664f1727e6844697537fc57ba565ab33f65.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/12095388dbb2b94e94b95ab98969e768ba050e2eb6bb44c5631042fe79df00f0.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/1333a33843b6cd56c88720e8657e45c9fd9a46c73a5f4e3f76aff63e11507254.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/14160434e5bae542287b9aee0d82ecc7a72425515329d8c0ac9fab17535063e7.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/15104a1432391708694c59c7d013f1284c1f60eda6cc96f993035c202cf16476.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/1651bfdbd177aabd5c4f7434ac20f2a86ac6ee9b1aa3051d0e7a4ffdcd49d47c.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/1668034f225691663d658817555f352eb78b5a320f5948de761c42c5c2b39a49.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/171143912edc06b8e28a1760edc742c609075b571c63c0dcf6abf2b63687361b.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/1786b1751d0e7d70e063db7827a82cc38aada6710d3e3c7e9a50cffd0968ac7b.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/19640ea5f390e2bff9379706f0756e008580429994b8f47dce4b32a5c7ac8d7d.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/1a912c383c8ce36d6a764ccbbcd565dfb9e9702209f775ebdaece5bbcaada488.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/1b594574fce78caa5e6480aff34d03d78e4cb81a375647d93934349519df6be6.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/1c94c764e766aa4abe0dc7e71636ff69f5d2b6d0e17b226d0d703cadcb65adab.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/1e4dc9288d2cc19253abb16d73acad36de08e8fe552c704288b9bbac2b31b03c.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/1e8a57b1d19d20056f0dca774937477d220917122eb6954c11e7280975dcf5d1.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/1fdc961e4adfe3e572942bb922b72c20da91b8a2a47d06c59247ddb3d3c3fe9f.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/1ff418fd3b4ffb5ed1abebbaf0ff2c9b7aebcc26d557c3a498e32f238aa17687.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/2257de2bf7bbfb48991c3aa53811a3fe6fa385c580c33e87e3b5ce23fb2ae01d.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/2324bb9ba88a65d513fb9513a1895680ea4ebade6662a60fe1b5edaeea4352dc.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/250912877d59d9d3cfcb4e3d2278d2c8c13ca661708941c76984ff937a4a27de.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/270302a31c6eb0a68d880c61ede36c93f68c0e150af2f3c6dab1fefb398692c6.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/2770f4df45320f9cfed18d990a0daa7d425ee7341d9a88ec4d24f83b8ed9f642.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/27739aea49a6239344941a699536af9b3a0d868ca565cd7162b9ae77666b7bd3.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/29be77965981bfb8f1ed8a65d3563f3c519115507f174c13b238b048577e201c.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/29d3d965bef924057b4a5e2587b5dbd8e0fa24d696385098d88b992c5ce5424a.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/29f9c58af115a14eaaa052a144b6aec3c1d0d0701a130fbcb887e8fe9a585161.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/2a3c31a03836eab852705a8a66bed81926487558a81aed66eefda014ad1277a4.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/2ab30201b2f3c6c8fc8d4e89c49be4362ead4d51ac96e2ba59f3cc9a536cf8ee.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/2c4a949399acac8308d34260270127faf94ee8cd8159c2695bb4bfb76a811dc5.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/2ce1ed9ab0bb6e4fc104a532be08e63efba937e72db4990ff56587864bbe1dd3.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/2f7961f6434390367d88fbc1d7affac18dd5a40949910e9746e3da348cfe601e.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/317bbf7f16a636d2b5002a1d7da710600c3b57646ebf544fd279cc990c0908da.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/31d7d0654941e8a4f4b41f201d0f58e38554b9c4d8564940c0e6c73d9f08b099.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/343bdefb5de79a7a2f954d77a313379a6fdf0f568e8f0237b6692f557ba2c94f.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/351f8d19fcf94c651f9a087c5fea69f54896b0108b95a17975e5161a6ee4164f.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/387f6670eae8762f77f89dae7d0722553475269d26883eb6023042243d99a60f.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/39127903f84db118e629d9da7290e58f6d907a8ae5559d0a2c5a06359562e55b.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/39a60d160afdfcc37ae4fc0ff7c23c4ee613785db90434f50716ac600de060bb.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/3ba3dcb0f1d35268f9c4ac8c917ff874523cd1c90dcbcb82414100ab5a3809fc.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/3c0197bc8500a227ad80c2a30b9d6e21619104c902a49983d35252055b65ad5b.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/3e94e0689e3bc40d813c49533d32ccf437ceb6ea7a291ef9c2b0164abcf4150f.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/3ed69325954871a2a6b8f7671428a4c6c114f322141fccca20e9a5f91e7199b0.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/3ee6167f866f4a7924a587a599117baf3db4c95c83b97dc21dfc7d1f02d19566.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/40425cfe198299ec3aaf7ab684d525f3ef74157bde2e2f98f1fe4414233db471.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/40b2c1ea918586287df5956532730acbde6f45754c6ef52164b87a65c2cbda52.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/42765d89c8ed15d2d13bee0c6628b3e8dafbad9a6a79f0caba26f220cf514a33.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/43c0a6bdcafe92403306e101bd4173ff8df7bd41b2f8d63623e04d3f0081f008.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/472d2c1bdc0e661eb816d2f711e8373ea080aa24873d13bd69018f29f1df4d90.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/47a1f27722bcd41a54961b8e1558fb43827d5c2678f2a75f66dc4cb3c3715f68.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/489cc524d4d429b39a846b24d282e64a1eb2ebe29ead8bad84002f272adadf23.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/49ec1ce850d64f952a9186372c1b5fb07f3bb44c58016cddea5e9cb7eccc79c1.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/4c11469f16dcc1d87e26d561743d64b235a161f13f93223c7f26b15421d9733e.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/4cc911c47b78e43382af1565a60f5edb29bf990e16497d4f54c38f2f45e78104.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/4cfa8fbdda1d7c85bb721fff58ba05ca9d37838451217a334360ecaa5a021197.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/4eb870738652db19ac97cb023f81c8f1528bf65f5232b056620fccfefb6fdd15.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/4ec0ad354d4158bc16258e3ecbe4ab59372b5a57bd52588fefcbbd8d1c6edda7.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/4f00155db249e64b196ebf79024c0a1367d26f95953d6bad5ce1419eebef1bde.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/4f9364e52c38c497f59a22768554d61bb7ced2f58663713040bb14a8330b1591.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/50cfe334d9f20dd59b41aa9f8f8866d21f8d46f8e308880a48fedb311e5d2231.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/511024c28b8a17b75822b5f2a2f30b53286c4f26d5bcfb1d8224c88b36ac82eb.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/5208e88801c61b836aebff68ae791b9a2668f2b0e87d705c217a0dcc1052bcc4.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/52b93289310a7e64119f4771d36ea6e47684010a35f023ca4c9f9c2a6b2c4569.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/52ba26b151260aa2f2017a4edc09fa8855887a3ec7f5be7646903f7b82cef6e2.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/552bbb92c553cae80569c574003725734ea3c125616824a17af03bec4371c496.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/558fad991843c7ccd0dfec1fa118b8fec2e5e5bfd5c934f96820d2a4d95ef249.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/55c3faa4c711a0441535029d9a32be9d165d856c0b83bd6ab6d0d35a7b7447e8.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/586b9990a17f8af5d237faaa2f5c0f256a0c5977c8834290c5dca088c73716da.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/59c40f56cb08a20180d649e6b16a16711dd6dd2c100b6332252d8d04e74a769b.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/5b79cfaa2f2d45994fede49aaf2e2f6564120f5b3ea484090740bf3222564370.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/5bce3c906031f12c105edf41fa02556ea92b3088158096e0c449adf978f8f227.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/60444670d9b18d20a3944455a8026f79aab70b6a86b5bdbb924ef506e4c55a99.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/61c64af5f8b54758da16fde7d5072e23e486cfc4ab012aed87680b295a0e4cf0.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/61eca18c66fcf4c6dc9db6b5cc990f63ae0dd176c8fdeef47371422d0bd9f75a.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/6257372a2ffcc0897a2350b75c622f1fcf20d288ae4f1b2cd9ad86c0cef33854.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/630913023402cc6b32d2bc198a8e07abcd3d142781b5869494057aebd45c36e5.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/631c5dfbb048ccfc943131622b419d607b4057daead9b1ebf735967bd6cb187c.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/63b45cfd4f2ba16e1f30ef233d0e343b8e796a8f194fd11c9b2b283e8543bbb2.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/6753d01606c7c93d0c22134140fbdae7c43934384df9ed697d2be0c1366c1984.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/67653be8ce4a2bf0d7be73a4b99e6cb3ad42361e387d3031e024419bea7425e7.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/67af738bd1fe701e2903226b3084c6b67fce699fc83f46de690d14745be15f98.json | created | Prompt01 evidence
- outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/cache/P01_G11A_V0_2024/i_methods/I6/6b8843b5134818ed44b8a4bda2ba77152aea639c014596a5960920215a0a2c6d.json | created | Prompt01 evidence

C. Files Modified
- AGENTS.md | modified | add Focused Candidate Optimisation Phase Rules
- src/nlpcc/evaluation/__init__.py | modified | add production-safe evaluation package
- src/nlpcc/evaluation/reference_official_semantics.py | modified | move local official-semantics replay out of tools imports
- src/nlpcc/news_overlay/grid_evaluator.py | modified | use production-safe evaluator import
- src/nlpcc/news_overlay/n_methods/architectures.py | modified | fix N4 side fields for G15B N4/I6/S2
- src/nlpcc/news_overlay/prompt22_runner.py | modified | use production-safe evaluator import
- src/nlpcc/news_overlay/prompt23_runner.py | modified | use production-safe evaluator import
- src/nlpcc/news_overlay/track_a_minor_enhancements.py | modified | use production-safe evaluator import
- src/nlpcc/news_overlay/track_b_parity_runner.py | modified | use production-safe evaluator import
- tests/test_nlpcc/test_news_overlay/test_scaffold.py | modified | prove N4 side fields and G15B nonzero overlay
- scripts/prompt01_no_bytecode_compile_smoke.py | modified | prove syntax without writing pycache
- scripts/run_prompt01_pipeline_repair_full_validation.py | modified | full local candidate rerun and evidence writer
- scripts/run_prompt01_checks_and_logs.py | modified | test runner, manifests, and implementation log writer

D. Files Read
- AGENTS.md | read | source truth or code context
- README.md | read | source truth or code context
- docs/REPO_STRUCTURE.md | read | source truth or code context
- docs/workflow/PROMPT_EXECUTION_PLAN.md | read | source truth or code context
- docs/context/current_decisions.md | read | source truth or code context
- docs/architecture/OFFICIAL_COMPATIBILITY.md | read | source truth or code context
- docs/architecture/REPO_POLICY.md | read | source truth or code context
- docs/strategy/B_LIST_HARDENING.md | read | source truth or code context
- NLPCC_tasks/README.md | read | source truth or code context
- NLPCC_tasks/dataset/README.md | read | source truth or code context
- docs/news_overlay/current_news_overlay_state.md | read | source truth or code context
- docs/news_overlay/final_candidate_pool.md | read | source truth or code context
- docs/news_overlay/next_phase_execution_plan.md | read | source truth or code context
- outputs/reports/news_overlay/prompt27_wrapup/** | read | source truth or code context
- outputs/reports/news_overlay/prompt26_complex_synthetic_retest/** | read | source truth or code context
- outputs/reports/focused_candidate_optimisation/presented/** | read | source truth or code context
- outputs/reports/focused_candidate_optimisation/reference/** | read | source truth or code context

E. Commands Run
- rtk python scripts/run_prompt01_pipeline_repair_full_validation.py | return_code=0 | duration_seconds=69.4 | output_log_path=outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/logs/prompt01_runner.log
- rtk --version | return_code=0 | duration_seconds=0.038 | output_log_path=outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/logs/rtk_version.log
- rtk git status | return_code=0 | duration_seconds=0.17 | output_log_path=outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/logs/git_status_after.log
- rtk git diff --name-only | return_code=0 | duration_seconds=0.265 | output_log_path=outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/logs/git_diff_name_only_after.log
- rtk python -m pytest tests/test_nlpcc/test_news_overlay -q | return_code=0 | duration_seconds=18.811 | output_log_path=outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/logs/news_overlay_pytest.log
- rtk python -m pytest tests/test_nlpcc -q | return_code=0 | duration_seconds=19.954 | output_log_path=outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/logs/full_pytest_tests_nlpcc.log
- rtk python -m pytest tests -q | return_code=0 | duration_seconds=21.336 | output_log_path=outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/logs/full_pytest_tests.log
- rtk python -m compileall src tests | return_code=1 | duration_seconds=0.801 | output_log_path=outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/logs/compileall_src_tests.log
- rtk python -B scripts/prompt01_no_bytecode_compile_smoke.py | return_code=0 | duration_seconds=0.464 | output_log_path=outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/logs/no_bytecode_compile_smoke.log
- rtk python -c "import sys; print(sys.version)" | return_code=0 | duration_seconds=0.141 | output_log_path=outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/logs/python_version.log
- rtk python -m pip check | return_code=1 | duration_seconds=1.144 | output_log_path=outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/logs/pip_check.log

F. Candidate Runs Completed
- G00B no_news 2024 | return=0.097399 | sharpe=0.507126 | overlay=False
- G00B no_news 2025 | return=0.284992 | sharpe=1.619708 | overlay=False
- G15B V0 2024 | return=0.084182 | sharpe=0.454367 | overlay=True
- G15B V4 2024 | return=0.079507 | sharpe=0.438296 | overlay=True
- G15B V0 2025 | return=0.278615 | sharpe=1.598599 | overlay=True
- G15B V4 2025 | return=0.277663 | sharpe=1.583053 | overlay=True
- G00A no_news 2024 | return=0.101916 | sharpe=0.576113 | overlay=False
- G00A no_news 2025 | return=0.331686 | sharpe=2.072983 | overlay=False
- G11A V0 2024 | return=0.071335 | sharpe=0.438846 | overlay=True
- G11A V0 2025 | return=0.329728 | sharpe=1.980358 | overlay=True
- G12A V3 2024 | return=0.094076 | sharpe=0.545176 | overlay=True
- G12A V3 2025 | return=0.325793 | sharpe=1.998866 | overlay=True
- G21B_repaired_lite repaired_lite 2024 | return=0.111155 | sharpe=0.561093 | overlay=True
- G21B_repaired_lite repaired_lite 2025 | return=0.266091 | sharpe=1.564853 | overlay=True

G. Pipeline Bugs Found
- G15B N4/I6/S2 was pipeline noop. N4 made event labels but did not emit relevance_by_sector or aspect_tone for I6.

H. Pipeline Bugs Fixed
- Fixed N4 to emit lexical relevance and aspect tone side fields. G15B now has nonzero overlay in local full run.

I. Tests Added or Updated
- Updated test_n4_label_attention_scores_are_probabilities.
- Added test_g15b_n4_i6_s2_stack_produces_nonzero_overlay.

J. Tests Run
- rtk python -m pytest tests/test_nlpcc/test_news_overlay -q | pass | log=outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/logs/news_overlay_pytest.log
- rtk python -m pytest tests/test_nlpcc -q | pass | log=outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/logs/full_pytest_tests_nlpcc.log
- rtk python -m pytest tests -q | pass | log=outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/logs/full_pytest_tests.log
- rtk python -m compileall src tests | fail | log=outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/logs/compileall_src_tests.log
- rtk python -m pip check | fail | log=outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/logs/pip_check.log

K. Failed / Blocked Runs
- rtk python -m compileall src tests | fail | log=outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/logs/compileall_src_tests.log
- rtk python -m pip check | fail | log=outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/logs/pip_check.log

L. Official Runtime Config Status
- official_runtime_changed: no

M. 2025 Tune Check
- 2025_tuned: no

N. Hidden 2026 Check
- hidden_2026_used: no

O. Artifacts
- phase_folder: outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation
- final_candidate_decision_table: outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/final_candidate_decision_table.csv
- full_checks_summary: outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/full_checks_summary.csv
- output_artifact_manifest: outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/output_artifact_manifest.csv

P. Caveats
- Evidence is local repo evidence. It is not official-server parity.
- Repo was dirty before Prompt01.
- No official runtime config was edited.

Q. Next Steps
- Package selected branch for parity prep only after dirty-state review.

Final table:
| candidate_id | candidate | variant | final_status | 2025_sharpe | decision |
| --- | --- | --- | --- | --- | --- |
| A1 | G12A | V3 | active_next_phase | 1.998866 | continue_active_with_proven_overlay |
| A2 | G11A | V0 | active_next_phase | 1.980358 | continue_active_with_proven_overlay |
| A0 | G00A | no_news | baseline_reference_only | 2.072983 | reference only |
| B1 | G15B | V0 | active_but_needs_more_evidence | 1.598599 | g15b_v0_active_after_fix |
| B2 | G15B | V4 | active_branch_selected | 1.583053 | g15b_v4_active_after_fix |
| B3 | G21B_repaired_lite | repaired_lite | active_but_needs_more_evidence | 1.564853 | continue_research_backup_only |
| B0 | G00B | no_news | baseline_reference_only | 1.619708 | reference only |
