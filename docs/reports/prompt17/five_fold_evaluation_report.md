# Five-Fold Evaluation Report

Folds are contiguous 80/20 validation slices over the bounded 2024 tensor horizon, replayed from fresh capital.

| candidate | track | folds | mean_return | mean_sharpe | worst_drawdown |
| --- | --- | --- | --- | --- | --- |
| hgf_mpc_macro_default | macro | 5 | -0.006786 | -5.621399 | 0.022697 |
| hgf_mpc_macro_drift60 | macro | 5 | -0.006786 | -5.621378 | 0.022697 |
| bsa_rp_macro_rule | macro | 5 | -0.011027 | -7.535828 | 0.030024 |
| s1_macro_default | macro | 5 | -0.011553 | -8.150262 | 0.026672 |
| robust_bl_macro_rule | macro | 5 | -0.011734 | -7.614688 | 0.029274 |
| dro_bl_rp_macro_rule | macro | 5 | -0.011734 | -7.614688 | 0.029274 |
| dro_bl_rp_macro_tau08 | macro | 5 | -0.011736 | -7.61465 | 0.029281 |
| s1_macro_momentum35 | macro | 5 | -0.011765 | -8.444293 | 0.026819 |
| leeqa_rank_top4 | sector | 5 | -0.011794 | -6.403382 | 0.031625 |
| risk_parity_macro | macro | 5 | -0.011797 | -7.334072 | 0.03049 |
| s0_macro_cash02 | macro | 5 | -0.011893 | -6.622025 | 0.027783 |
| s0_macro_cash03 | macro | 5 | -0.011893 | -6.622025 | 0.027783 |
| leeqa_rank_rule | sector | 5 | -0.012747 | -7.748228 | 0.032458 |
| s1_sector_default | sector | 5 | -0.012871 | -9.20622 | 0.031126 |
| s1_sector_trend60 | sector | 5 | -0.013084 | -9.433423 | 0.031304 |
