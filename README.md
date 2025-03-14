# 🚀 Projet MPI + OpenMP

Ce dépôt contient les résultats et analyses des différentes étapes réalisées pour évaluer les performances d'une application parallèle utilisant MPI et OpenMP dans le cadre du cours **Systèmes parallèles et distribués (CSC_4OS02_TA)**.

## 📁 Structure du projet

Chaque dossier nommé `Etape_<X>` correspond à une étape spécifique du projet.

À l'intérieur de chaque dossier, vous trouverez :
- Un fichier **`README.md`** qui explique clairement :
  - Ce qui a été réalisé dans cette étape.
  - Les résultats obtenus et leur interprétation.

En particulier, le dossier **`Etape_1`** est la base de notre travail. Il contient, en plus du README principal :
- Des fichiers Markdown complémentaires (**`*.md`**) fournissant des explications détaillées sur :
  - Ce que nous avons fait.
  - Comment nous l'avons réalisé.

## 🖥️ Détails du processeur

Le projet a été simulé dans ce processeur ci-dessous:

| Category | Value |
|----------|-------|
| Architecture | x86_64 |
| CPU op-mode(s) | 32-bit, 64-bit |
| Address sizes | 43 bits physical, 48 bits virtual |
| Byte Order | Little Endian |
| CPU(s) | 12 |
| On-line CPU(s) list | 0-11 |
| Vendor ID | AuthenticAMD |
| Model name | AMD Ryzen 5 3600X 6-Core Processor |
| CPU family | 23 |
| Model | 113 |
| Thread(s) per core | 2 |
| Core(s) per socket | 6 |
| Socket(s) | 1 |
| Stepping | 0 |
| Frequency boost | enabled |
| CPU(s) scaling MHz | 48% |
| CPU max MHz | 4409.0000 |
| CPU min MHz | 550.0000 |
| BogoMIPS | 7602.42 |
| Flags | fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush mmx fxsr sse sse2 ht syscall nx mmxext fxsr_opt pdpe1gb rdtscp lm constant_tsc rep_good nopl xtopology nonstop_tsc cpuid extd_apicid aperfmperf rapl pni pclmulqdq monitor ssse3 fma cx16 sse4_1 sse4_2 x2apic movbe popcnt aes xsave avx f16c rdrand lahf_lm cmp_legacy svm extapic cr8_legacy abm sse4a misalignsse 3dnowprefetch osvw ibs skinit wdt tce topoext perfctr_core perfctr_nb bpext perfctr_llc mwaitx cpb cat_l3 cdp_l3 hw_pstate ssbd mba ibpb stibp vmmcall fsgsbase bmi1 avx2 smep bmi2 cqm rdt_a rdseed adx smap clflushopt clwb sha_ni xsaveopt xsavec xgetbv1 cqm_llc cqm_occup_llc cqm_mbm_total cqm_mbm_local clzero irperf xsaveerptr rdpru wbnoinvd arat npt lbrv svm_lock nrip_save tsc_scale vmcb_clean flushbyasid decodeassists pausefilter pfthreshold avic v_vmsave_vmload vgif v_spec_ctrl umip rdpid overflow_recov succor smca sev sev_es |
| **Virtualization features** | |
| Virtualization | AMD-V |
| **Caches (sum of all)** | |
| L1d | 192 KiB (6 instances) |
| L1i | 192 KiB (6 instances) |
| L2 | 3 MiB (6 instances) |
| L3 | 32 MiB (2 instances) |
| **NUMA** | |
| NUMA node(s) | 1 |
| NUMA node0 CPU(s) | 0-11 |
| **Vulnerabilities** | |
| Gather data sampling | Not affected |
| Itlb multihit | Not affected |
| L1tf | Not affected |
| Mds | Not affected |
| Meltdown | Not affected |
| Mmio stale data | Not affected |
| Reg file data sampling | Not affected |
| Retbleed | Mitigation; untrained return thunk; SMT enabled with STIBP protection |
| Spec rstack overflow | Mitigation; Safe RET |
| Spec store bypass | Mitigation; Speculative Store Bypass disabled via prctl |
| Spectre v1 | Mitigation; usercopy/swapgs barriers and __user pointer sanitization |
| Spectre v2 | Mitigation; Retpolines; IBPB conditional; STIBP always-on; RSB filling; PBRSB-eIBRS Not affected; BHI Not affected |
| Srbds | Not affected |
| Tsx async abort | Not affected |

## **Students**
Ce projet a été réalisé par :
- **Lucas de Oliveira Martim**
- **Rodrigo Botelho Zuiani**

