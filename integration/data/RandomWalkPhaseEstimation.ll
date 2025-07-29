%Result = type opaque
%Qubit = type opaque

@0 = internal constant [3 x i8] c"d0\00"

define void @ENTRYPOINT__main() #0 {
block_0:
  call void @__quantum__qis__h__body(%Qubit* inttoptr (i64 1 to %Qubit*))
  call void @__quantum__qis__rz__body(double 1.8891062129786873, %Qubit* inttoptr (i64 1 to %Qubit*))
  call void @__quantum__qis__rz__body(double -0.3183098861837907, %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__cx__body(%Qubit* inttoptr (i64 1 to %Qubit*), %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__rz__body(double 0.3183098861837907, %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__cx__body(%Qubit* inttoptr (i64 1 to %Qubit*), %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__h__body(%Qubit* inttoptr (i64 1 to %Qubit*))
  call void @__quantum__qis__mresetz__body(%Qubit* inttoptr (i64 1 to %Qubit*), %Result* inttoptr (i64 0 to %Result*))
  %var_4 = call i1 @__quantum__rt__read_result(%Result* inttoptr (i64 0 to %Result*))
  %var_5 = icmp eq i1 %var_4, false
  br i1 %var_5, label %block_1, label %block_2
block_1:
  br label %block_3
block_2:
  br label %block_3
block_3:
  %var_216 = phi double [1.4527361323650898, %block_1], [-0.4527361323650899, %block_2]
  %var_6 = fsub double %var_216, -1.9617321596518258
  %var_8 = fmul double %var_6, -0.8007190579338244
  %var_9 = fmul double -1.0, %var_8
  call void @__quantum__qis__h__body(%Qubit* inttoptr (i64 1 to %Qubit*))
  call void @__quantum__qis__rz__body(double %var_9, %Qubit* inttoptr (i64 1 to %Qubit*))
  call void @__quantum__qis__rz__body(double -0.4003595289669122, %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__cx__body(%Qubit* inttoptr (i64 1 to %Qubit*), %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__rz__body(double 0.4003595289669122, %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__cx__body(%Qubit* inttoptr (i64 1 to %Qubit*), %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__h__body(%Qubit* inttoptr (i64 1 to %Qubit*))
  call void @__quantum__qis__mresetz__body(%Qubit* inttoptr (i64 1 to %Qubit*), %Result* inttoptr (i64 1 to %Result*))
  %var_11 = call i1 @__quantum__rt__read_result(%Result* inttoptr (i64 1 to %Result*))
  %var_12 = icmp eq i1 %var_11, false
  br i1 %var_12, label %block_4, label %block_5
block_4:
  %var_13 = fsub double %var_216, -0.757482482404909
  br label %block_6
block_5:
  %var_14 = fadd double %var_216, -0.757482482404909
  br label %block_6
block_6:
  %var_217 = phi double [%var_13, %block_4], [%var_14, %block_5]
  %var_15 = fsub double %var_217, -1.5596949623583491
  %var_17 = fmul double %var_15, -1.0071176510179667
  %var_18 = fmul double -1.0, %var_17
  call void @__quantum__qis__h__body(%Qubit* inttoptr (i64 1 to %Qubit*))
  call void @__quantum__qis__rz__body(double %var_18, %Qubit* inttoptr (i64 1 to %Qubit*))
  call void @__quantum__qis__rz__body(double -0.5035588255089833, %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__cx__body(%Qubit* inttoptr (i64 1 to %Qubit*), %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__rz__body(double 0.5035588255089833, %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__cx__body(%Qubit* inttoptr (i64 1 to %Qubit*), %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__h__body(%Qubit* inttoptr (i64 1 to %Qubit*))
  call void @__quantum__qis__mresetz__body(%Qubit* inttoptr (i64 1 to %Qubit*), %Result* inttoptr (i64 2 to %Result*))
  %var_20 = call i1 @__quantum__rt__read_result(%Result* inttoptr (i64 2 to %Result*))
  %var_21 = icmp eq i1 %var_20, false
  br i1 %var_21, label %block_7, label %block_8
block_7:
  %var_22 = fsub double %var_217, -0.6022440964067793
  br label %block_9
block_8:
  %var_23 = fadd double %var_217, -0.6022440964067793
  br label %block_9
block_9:
  %var_218 = phi double [%var_22, %block_7], [%var_23, %block_8]
  %var_24 = fsub double %var_218, -1.2400512290310655
  %var_26 = fmul double %var_24, -1.266718898397661
  %var_27 = fmul double -1.0, %var_26
  call void @__quantum__qis__h__body(%Qubit* inttoptr (i64 1 to %Qubit*))
  call void @__quantum__qis__rz__body(double %var_27, %Qubit* inttoptr (i64 1 to %Qubit*))
  call void @__quantum__qis__rz__body(double -0.6333594491988305, %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__cx__body(%Qubit* inttoptr (i64 1 to %Qubit*), %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__rz__body(double 0.6333594491988305, %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__cx__body(%Qubit* inttoptr (i64 1 to %Qubit*), %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__h__body(%Qubit* inttoptr (i64 1 to %Qubit*))
  call void @__quantum__qis__mresetz__body(%Qubit* inttoptr (i64 1 to %Qubit*), %Result* inttoptr (i64 3 to %Result*))
  %var_29 = call i1 @__quantum__rt__read_result(%Result* inttoptr (i64 3 to %Result*))
  %var_30 = icmp eq i1 %var_29, false
  br i1 %var_30, label %block_10, label %block_11
block_10:
  %var_31 = fsub double %var_218, -0.47882025008063417
  br label %block_12
block_11:
  %var_32 = fadd double %var_218, -0.47882025008063417
  br label %block_12
block_12:
  %var_219 = phi double [%var_31, %block_10], [%var_32, %block_11]
  %var_33 = fsub double %var_219, -0.985915251208046
  %var_35 = fmul double %var_33, -1.5932366649873744
  %var_36 = fmul double -1.0, %var_35
  call void @__quantum__qis__h__body(%Qubit* inttoptr (i64 1 to %Qubit*))
  call void @__quantum__qis__rz__body(double %var_36, %Qubit* inttoptr (i64 1 to %Qubit*))
  call void @__quantum__qis__rz__body(double -0.7966183324936872, %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__cx__body(%Qubit* inttoptr (i64 1 to %Qubit*), %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__rz__body(double 0.7966183324936872, %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__cx__body(%Qubit* inttoptr (i64 1 to %Qubit*), %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__h__body(%Qubit* inttoptr (i64 1 to %Qubit*))
  call void @__quantum__qis__mresetz__body(%Qubit* inttoptr (i64 1 to %Qubit*), %Result* inttoptr (i64 4 to %Result*))
  %var_38 = call i1 @__quantum__rt__read_result(%Result* inttoptr (i64 4 to %Result*))
  %var_39 = icmp eq i1 %var_38, false
  br i1 %var_39, label %block_13, label %block_14
block_13:
  %var_40 = fsub double %var_219, -0.38069087477185315
  br label %block_15
block_14:
  %var_41 = fadd double %var_219, -0.38069087477185315
  br label %block_15
block_15:
  %var_220 = phi double [%var_40, %block_13], [%var_41, %block_14]
  %var_42 = fsub double %var_220, -0.7838618758711569
  %var_44 = fmul double %var_42, -2.0039197914162723
  %var_45 = fmul double -1.0, %var_44
  call void @__quantum__qis__h__body(%Qubit* inttoptr (i64 1 to %Qubit*))
  call void @__quantum__qis__rz__body(double %var_45, %Qubit* inttoptr (i64 1 to %Qubit*))
  call void @__quantum__qis__rz__body(double -1.0019598957081362, %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__cx__body(%Qubit* inttoptr (i64 1 to %Qubit*), %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__rz__body(double 1.0019598957081362, %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__cx__body(%Qubit* inttoptr (i64 1 to %Qubit*), %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__h__body(%Qubit* inttoptr (i64 1 to %Qubit*))
  call void @__quantum__qis__mresetz__body(%Qubit* inttoptr (i64 1 to %Qubit*), %Result* inttoptr (i64 5 to %Result*))
  %var_47 = call i1 @__quantum__rt__read_result(%Result* inttoptr (i64 5 to %Result*))
  %var_48 = icmp eq i1 %var_47, false
  br i1 %var_48, label %block_16, label %block_17
block_16:
  %var_49 = fsub double %var_220, -0.30267212405940025
  br label %block_18
block_17:
  %var_50 = fadd double %var_220, -0.30267212405940025
  br label %block_18
block_18:
  %var_221 = phi double [%var_49, %block_16], [%var_50, %block_17]
  %var_51 = fsub double %var_221, -0.6232172995512278
  %var_53 = fmul double %var_51, -2.5204632925401946
  %var_54 = fmul double -1.0, %var_53
  call void @__quantum__qis__h__body(%Qubit* inttoptr (i64 1 to %Qubit*))
  call void @__quantum__qis__rz__body(double %var_54, %Qubit* inttoptr (i64 1 to %Qubit*))
  call void @__quantum__qis__rz__body(double -1.2602316462700973, %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__cx__body(%Qubit* inttoptr (i64 1 to %Qubit*), %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__rz__body(double 1.2602316462700973, %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__cx__body(%Qubit* inttoptr (i64 1 to %Qubit*), %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__h__body(%Qubit* inttoptr (i64 1 to %Qubit*))
  call void @__quantum__qis__mresetz__body(%Qubit* inttoptr (i64 1 to %Qubit*), %Result* inttoptr (i64 6 to %Result*))
  %var_56 = call i1 @__quantum__rt__read_result(%Result* inttoptr (i64 6 to %Result*))
  %var_57 = icmp eq i1 %var_56, false
  br i1 %var_57, label %block_19, label %block_20
block_19:
  %var_58 = fsub double %var_221, -0.24064252850171627
  br label %block_21
block_20:
  %var_59 = fadd double %var_221, -0.24064252850171627
  br label %block_21
block_21:
  %var_222 = phi double [%var_58, %block_19], [%var_59, %block_20]
  %var_60 = fsub double %var_222, -0.4954952070200772
  %var_62 = fmul double %var_60, -3.1701544324549817
  %var_63 = fmul double -1.0, %var_62
  call void @__quantum__qis__h__body(%Qubit* inttoptr (i64 1 to %Qubit*))
  call void @__quantum__qis__rz__body(double %var_63, %Qubit* inttoptr (i64 1 to %Qubit*))
  call void @__quantum__qis__rz__body(double -1.5850772162274909, %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__cx__body(%Qubit* inttoptr (i64 1 to %Qubit*), %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__rz__body(double 1.5850772162274909, %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__cx__body(%Qubit* inttoptr (i64 1 to %Qubit*), %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__h__body(%Qubit* inttoptr (i64 1 to %Qubit*))
  call void @__quantum__qis__mresetz__body(%Qubit* inttoptr (i64 1 to %Qubit*), %Result* inttoptr (i64 7 to %Result*))
  %var_65 = call i1 @__quantum__rt__read_result(%Result* inttoptr (i64 7 to %Result*))
  %var_66 = icmp eq i1 %var_65, false
  br i1 %var_66, label %block_22, label %block_23
block_22:
  %var_67 = fsub double %var_222, -0.19132527220225462
  br label %block_24
block_23:
  %var_68 = fadd double %var_222, -0.19132527220225462
  br label %block_24
block_24:
  %var_223 = phi double [%var_67, %block_22], [%var_68, %block_23]
  %var_69 = fsub double %var_223, -0.3939484676639468
  %var_71 = fmul double %var_69, -3.987314219317757
  %var_72 = fmul double -1.0, %var_71
  call void @__quantum__qis__h__body(%Qubit* inttoptr (i64 1 to %Qubit*))
  call void @__quantum__qis__rz__body(double %var_72, %Qubit* inttoptr (i64 1 to %Qubit*))
  call void @__quantum__qis__rz__body(double -1.9936571096588784, %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__cx__body(%Qubit* inttoptr (i64 1 to %Qubit*), %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__rz__body(double 1.9936571096588784, %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__cx__body(%Qubit* inttoptr (i64 1 to %Qubit*), %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__h__body(%Qubit* inttoptr (i64 1 to %Qubit*))
  call void @__quantum__qis__mresetz__body(%Qubit* inttoptr (i64 1 to %Qubit*), %Result* inttoptr (i64 8 to %Result*))
  %var_74 = call i1 @__quantum__rt__read_result(%Result* inttoptr (i64 8 to %Result*))
  %var_75 = icmp eq i1 %var_74, false
  br i1 %var_75, label %block_25, label %block_26
block_25:
  %var_76 = fsub double %var_223, -0.15211508959442202
  br label %block_27
block_26:
  %var_77 = fadd double %var_223, -0.15211508959442202
  br label %block_27
block_27:
  %var_224 = phi double [%var_76, %block_25], [%var_77, %block_26]
  %var_78 = fsub double %var_224, -0.31321270715840305
  %var_80 = fmul double %var_78, -5.015110469322331
  %var_81 = fmul double -1.0, %var_80
  call void @__quantum__qis__h__body(%Qubit* inttoptr (i64 1 to %Qubit*))
  call void @__quantum__qis__rz__body(double %var_81, %Qubit* inttoptr (i64 1 to %Qubit*))
  call void @__quantum__qis__rz__body(double -2.5075552346611656, %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__cx__body(%Qubit* inttoptr (i64 1 to %Qubit*), %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__rz__body(double 2.5075552346611656, %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__cx__body(%Qubit* inttoptr (i64 1 to %Qubit*), %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__h__body(%Qubit* inttoptr (i64 1 to %Qubit*))
  call void @__quantum__qis__mresetz__body(%Qubit* inttoptr (i64 1 to %Qubit*), %Result* inttoptr (i64 9 to %Result*))
  %var_83 = call i1 @__quantum__rt__read_result(%Result* inttoptr (i64 9 to %Result*))
  %var_84 = icmp eq i1 %var_83, false
  br i1 %var_84, label %block_28, label %block_29
block_28:
  %var_85 = fsub double %var_224, -0.1209406379825151
  br label %block_30
block_29:
  %var_86 = fadd double %var_224, -0.1209406379825151
  br label %block_30
block_30:
  %var_225 = phi double [%var_85, %block_28], [%var_86, %block_29]
  %var_87 = fsub double %var_225, -0.24902292552938804
  %var_89 = fmul double %var_87, -6.307838217929544
  %var_90 = fmul double -1.0, %var_89
  call void @__quantum__qis__h__body(%Qubit* inttoptr (i64 1 to %Qubit*))
  call void @__quantum__qis__rz__body(double %var_90, %Qubit* inttoptr (i64 1 to %Qubit*))
  call void @__quantum__qis__rz__body(double -3.153919108964772, %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__cx__body(%Qubit* inttoptr (i64 1 to %Qubit*), %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__rz__body(double 3.153919108964772, %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__cx__body(%Qubit* inttoptr (i64 1 to %Qubit*), %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__h__body(%Qubit* inttoptr (i64 1 to %Qubit*))
  call void @__quantum__qis__mresetz__body(%Qubit* inttoptr (i64 1 to %Qubit*), %Result* inttoptr (i64 10 to %Result*))
  %var_92 = call i1 @__quantum__rt__read_result(%Result* inttoptr (i64 10 to %Result*))
  %var_93 = icmp eq i1 %var_92, false
  br i1 %var_93, label %block_31, label %block_32
block_31:
  %var_94 = fsub double %var_225, -0.09615507544068216
  br label %block_33
block_32:
  %var_95 = fadd double %var_225, -0.09615507544068216
  br label %block_33
block_33:
  %var_226 = phi double [%var_94, %block_31], [%var_95, %block_32]
  %var_96 = fsub double %var_226, -0.1979881914811751
  %var_98 = fmul double %var_96, -7.933787944844424
  %var_99 = fmul double -1.0, %var_98
  call void @__quantum__qis__h__body(%Qubit* inttoptr (i64 1 to %Qubit*))
  call void @__quantum__qis__rz__body(double %var_99, %Qubit* inttoptr (i64 1 to %Qubit*))
  call void @__quantum__qis__rz__body(double -3.966893972422212, %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__cx__body(%Qubit* inttoptr (i64 1 to %Qubit*), %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__rz__body(double 3.966893972422212, %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__cx__body(%Qubit* inttoptr (i64 1 to %Qubit*), %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__h__body(%Qubit* inttoptr (i64 1 to %Qubit*))
  call void @__quantum__qis__mresetz__body(%Qubit* inttoptr (i64 1 to %Qubit*), %Result* inttoptr (i64 11 to %Result*))
  %var_101 = call i1 @__quantum__rt__read_result(%Result* inttoptr (i64 11 to %Result*))
  %var_102 = icmp eq i1 %var_101, false
  br i1 %var_102, label %block_34, label %block_35
block_34:
  %var_103 = fsub double %var_226, -0.07644906366658973
  br label %block_36
block_35:
  %var_104 = fadd double %var_226, -0.07644906366658973
  br label %block_36
block_36:
  %var_227 = phi double [%var_103, %block_34], [%var_104, %block_35]
  %var_105 = fsub double %var_227, -0.15741251084675906
  %var_107 = fmul double %var_105, -9.978853131464662
  %var_108 = fmul double -1.0, %var_107
  call void @__quantum__qis__h__body(%Qubit* inttoptr (i64 1 to %Qubit*))
  call void @__quantum__qis__rz__body(double %var_108, %Qubit* inttoptr (i64 1 to %Qubit*))
  call void @__quantum__qis__rz__body(double -4.989426565732331, %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__cx__body(%Qubit* inttoptr (i64 1 to %Qubit*), %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__rz__body(double 4.989426565732331, %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__cx__body(%Qubit* inttoptr (i64 1 to %Qubit*), %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__h__body(%Qubit* inttoptr (i64 1 to %Qubit*))
  call void @__quantum__qis__mresetz__body(%Qubit* inttoptr (i64 1 to %Qubit*), %Result* inttoptr (i64 12 to %Result*))
  %var_110 = call i1 @__quantum__rt__read_result(%Result* inttoptr (i64 12 to %Result*))
  %var_111 = icmp eq i1 %var_110, false
  br i1 %var_111, label %block_37, label %block_38
block_37:
  %var_112 = fsub double %var_227, -0.06078160002176612
  br label %block_39
block_38:
  %var_113 = fadd double %var_227, -0.06078160002176612
  br label %block_39
block_39:
  %var_228 = phi double [%var_112, %block_37], [%var_113, %block_38]
  %var_114 = fsub double %var_228, -0.1251524062405359
  %var_116 = fmul double %var_114, -12.551067725984543
  %var_117 = fmul double -1.0, %var_116
  call void @__quantum__qis__h__body(%Qubit* inttoptr (i64 1 to %Qubit*))
  call void @__quantum__qis__rz__body(double %var_117, %Qubit* inttoptr (i64 1 to %Qubit*))
  call void @__quantum__qis__rz__body(double -6.275533862992272, %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__cx__body(%Qubit* inttoptr (i64 1 to %Qubit*), %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__rz__body(double 6.275533862992272, %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__cx__body(%Qubit* inttoptr (i64 1 to %Qubit*), %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__h__body(%Qubit* inttoptr (i64 1 to %Qubit*))
  call void @__quantum__qis__mresetz__body(%Qubit* inttoptr (i64 1 to %Qubit*), %Result* inttoptr (i64 13 to %Result*))
  %var_119 = call i1 @__quantum__rt__read_result(%Result* inttoptr (i64 13 to %Result*))
  %var_120 = icmp eq i1 %var_119, false
  br i1 %var_120, label %block_40, label %block_41
block_40:
  %var_121 = fsub double %var_228, -0.04832502484684468
  br label %block_42
block_41:
  %var_122 = fadd double %var_228, -0.04832502484684468
  br label %block_42
block_42:
  %var_229 = phi double [%var_121, %block_40], [%var_122, %block_41]
  %var_123 = fsub double %var_229, -0.09950368432305973
  %var_125 = fmul double %var_123, -15.78631321524713
  %var_126 = fmul double -1.0, %var_125
  call void @__quantum__qis__h__body(%Qubit* inttoptr (i64 1 to %Qubit*))
  call void @__quantum__qis__rz__body(double %var_126, %Qubit* inttoptr (i64 1 to %Qubit*))
  call void @__quantum__qis__rz__body(double -7.893156607623565, %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__cx__body(%Qubit* inttoptr (i64 1 to %Qubit*), %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__rz__body(double 7.893156607623565, %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__cx__body(%Qubit* inttoptr (i64 1 to %Qubit*), %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__h__body(%Qubit* inttoptr (i64 1 to %Qubit*))
  call void @__quantum__qis__mresetz__body(%Qubit* inttoptr (i64 1 to %Qubit*), %Result* inttoptr (i64 14 to %Result*))
  %var_128 = call i1 @__quantum__rt__read_result(%Result* inttoptr (i64 14 to %Result*))
  %var_129 = icmp eq i1 %var_128, false
  br i1 %var_129, label %block_43, label %block_44
block_43:
  %var_130 = fsub double %var_229, -0.038421298972252674
  br label %block_45
block_44:
  %var_131 = fadd double %var_229, -0.038421298972252674
  br label %block_45
block_45:
  %var_230 = phi double [%var_130, %block_43], [%var_131, %block_44]
  %var_132 = fsub double %var_230, -0.07911140897150623
  %var_134 = fmul double %var_132, -19.85549678884691
  %var_135 = fmul double -1.0, %var_134
  call void @__quantum__qis__h__body(%Qubit* inttoptr (i64 1 to %Qubit*))
  call void @__quantum__qis__rz__body(double %var_135, %Qubit* inttoptr (i64 1 to %Qubit*))
  call void @__quantum__qis__rz__body(double -9.927748394423455, %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__cx__body(%Qubit* inttoptr (i64 1 to %Qubit*), %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__rz__body(double 9.927748394423455, %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__cx__body(%Qubit* inttoptr (i64 1 to %Qubit*), %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__h__body(%Qubit* inttoptr (i64 1 to %Qubit*))
  call void @__quantum__qis__mresetz__body(%Qubit* inttoptr (i64 1 to %Qubit*), %Result* inttoptr (i64 15 to %Result*))
  %var_137 = call i1 @__quantum__rt__read_result(%Result* inttoptr (i64 15 to %Result*))
  %var_138 = icmp eq i1 %var_137, false
  br i1 %var_138, label %block_46, label %block_47
block_46:
  %var_139 = fsub double %var_230, -0.0305472417115914
  br label %block_48
block_47:
  %var_140 = fadd double %var_230, -0.0305472417115914
  br label %block_48
block_48:
  %var_231 = phi double [%var_139, %block_46], [%var_140, %block_47]
  %var_141 = fsub double %var_231, -0.06289832453979291
  %var_143 = fmul double %var_141, -24.973579793864385
  %var_144 = fmul double -1.0, %var_143
  call void @__quantum__qis__h__body(%Qubit* inttoptr (i64 1 to %Qubit*))
  call void @__quantum__qis__rz__body(double %var_144, %Qubit* inttoptr (i64 1 to %Qubit*))
  call void @__quantum__qis__rz__body(double -12.486789896932192, %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__cx__body(%Qubit* inttoptr (i64 1 to %Qubit*), %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__rz__body(double 12.486789896932192, %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__cx__body(%Qubit* inttoptr (i64 1 to %Qubit*), %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__h__body(%Qubit* inttoptr (i64 1 to %Qubit*))
  call void @__quantum__qis__mresetz__body(%Qubit* inttoptr (i64 1 to %Qubit*), %Result* inttoptr (i64 16 to %Result*))
  %var_146 = call i1 @__quantum__rt__read_result(%Result* inttoptr (i64 16 to %Result*))
  %var_147 = icmp eq i1 %var_146, false
  br i1 %var_147, label %block_49, label %block_50
block_49:
  %var_148 = fsub double %var_231, -0.02428689297725945
  br label %block_51
block_50:
  %var_149 = fadd double %var_231, -0.02428689297725945
  br label %block_51
block_51:
  %var_232 = phi double [%var_148, %block_49], [%var_149, %block_50]
  %var_150 = fsub double %var_232, -0.050007948048783085
  %var_152 = fmul double %var_150, -31.41093342327452
  %var_153 = fmul double -1.0, %var_152
  call void @__quantum__qis__h__body(%Qubit* inttoptr (i64 1 to %Qubit*))
  call void @__quantum__qis__rz__body(double %var_153, %Qubit* inttoptr (i64 1 to %Qubit*))
  call void @__quantum__qis__rz__body(double -15.70546671163726, %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__cx__body(%Qubit* inttoptr (i64 1 to %Qubit*), %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__rz__body(double 15.70546671163726, %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__cx__body(%Qubit* inttoptr (i64 1 to %Qubit*), %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__h__body(%Qubit* inttoptr (i64 1 to %Qubit*))
  call void @__quantum__qis__mresetz__body(%Qubit* inttoptr (i64 1 to %Qubit*), %Result* inttoptr (i64 17 to %Result*))
  %var_155 = call i1 @__quantum__rt__read_result(%Result* inttoptr (i64 17 to %Result*))
  %var_156 = icmp eq i1 %var_155, false
  br i1 %var_156, label %block_52, label %block_53
block_52:
  %var_157 = fsub double %var_232, -0.01930953950140218
  br label %block_54
block_53:
  %var_158 = fadd double %var_232, -0.01930953950140218
  br label %block_54
block_54:
  %var_233 = phi double [%var_157, %block_52], [%var_158, %block_53]
  %var_159 = fsub double %var_233, -0.03975932405747388
  %var_161 = fmul double %var_159, -39.50762152103593
  %var_162 = fmul double -1.0, %var_161
  call void @__quantum__qis__h__body(%Qubit* inttoptr (i64 1 to %Qubit*))
  call void @__quantum__qis__rz__body(double %var_162, %Qubit* inttoptr (i64 1 to %Qubit*))
  call void @__quantum__qis__rz__body(double -19.753810760517965, %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__cx__body(%Qubit* inttoptr (i64 1 to %Qubit*), %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__rz__body(double 19.753810760517965, %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__cx__body(%Qubit* inttoptr (i64 1 to %Qubit*), %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__h__body(%Qubit* inttoptr (i64 1 to %Qubit*))
  call void @__quantum__qis__mresetz__body(%Qubit* inttoptr (i64 1 to %Qubit*), %Result* inttoptr (i64 18 to %Result*))
  %var_164 = call i1 @__quantum__rt__read_result(%Result* inttoptr (i64 18 to %Result*))
  %var_165 = icmp eq i1 %var_164, false
  br i1 %var_165, label %block_55, label %block_56
block_55:
  %var_166 = fsub double %var_233, -0.015352244360994617
  br label %block_57
block_56:
  %var_167 = fadd double %var_233, -0.015352244360994617
  br label %block_57
block_57:
  %var_234 = phi double [%var_166, %block_55], [%var_167, %block_56]
  %var_168 = fsub double %var_234, -0.03161105206646624
  %var_170 = fmul double %var_168, -49.69136501664349
  %var_171 = fmul double -1.0, %var_170
  call void @__quantum__qis__h__body(%Qubit* inttoptr (i64 1 to %Qubit*))
  call void @__quantum__qis__rz__body(double %var_171, %Qubit* inttoptr (i64 1 to %Qubit*))
  call void @__quantum__qis__rz__body(double -24.845682508321744, %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__cx__body(%Qubit* inttoptr (i64 1 to %Qubit*), %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__rz__body(double 24.845682508321744, %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__cx__body(%Qubit* inttoptr (i64 1 to %Qubit*), %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__h__body(%Qubit* inttoptr (i64 1 to %Qubit*))
  call void @__quantum__qis__mresetz__body(%Qubit* inttoptr (i64 1 to %Qubit*), %Result* inttoptr (i64 19 to %Result*))
  %var_173 = call i1 @__quantum__rt__read_result(%Result* inttoptr (i64 19 to %Result*))
  %var_174 = icmp eq i1 %var_173, false
  br i1 %var_174, label %block_58, label %block_59
block_58:
  %var_175 = fsub double %var_234, -0.012205956900348456
  br label %block_60
block_59:
  %var_176 = fadd double %var_234, -0.012205956900348456
  br label %block_60
block_60:
  %var_235 = phi double [%var_175, %block_58], [%var_176, %block_59]
  %var_177 = fsub double %var_235, -0.025132686141856108
  %var_179 = fmul double %var_177, -62.50013699008814
  %var_180 = fmul double -1.0, %var_179
  call void @__quantum__qis__h__body(%Qubit* inttoptr (i64 1 to %Qubit*))
  call void @__quantum__qis__rz__body(double %var_180, %Qubit* inttoptr (i64 1 to %Qubit*))
  call void @__quantum__qis__rz__body(double -31.25006849504407, %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__cx__body(%Qubit* inttoptr (i64 1 to %Qubit*), %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__rz__body(double 31.25006849504407, %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__cx__body(%Qubit* inttoptr (i64 1 to %Qubit*), %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__h__body(%Qubit* inttoptr (i64 1 to %Qubit*))
  call void @__quantum__qis__mresetz__body(%Qubit* inttoptr (i64 1 to %Qubit*), %Result* inttoptr (i64 20 to %Result*))
  %var_182 = call i1 @__quantum__rt__read_result(%Result* inttoptr (i64 20 to %Result*))
  %var_183 = icmp eq i1 %var_182, false
  br i1 %var_183, label %block_61, label %block_62
block_61:
  %var_184 = fsub double %var_235, -0.009704469284744492
  br label %block_63
block_62:
  %var_185 = fadd double %var_235, -0.009704469284744492
  br label %block_63
block_63:
  %var_236 = phi double [%var_184, %block_61], [%var_185, %block_62]
  %var_186 = fsub double %var_236, -0.019981995897413278
  %var_188 = fmul double %var_186, -78.6105819888713
  %var_189 = fmul double -1.0, %var_188
  call void @__quantum__qis__h__body(%Qubit* inttoptr (i64 1 to %Qubit*))
  call void @__quantum__qis__rz__body(double %var_189, %Qubit* inttoptr (i64 1 to %Qubit*))
  call void @__quantum__qis__rz__body(double -39.30529099443565, %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__cx__body(%Qubit* inttoptr (i64 1 to %Qubit*), %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__rz__body(double 39.30529099443565, %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__cx__body(%Qubit* inttoptr (i64 1 to %Qubit*), %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__h__body(%Qubit* inttoptr (i64 1 to %Qubit*))
  call void @__quantum__qis__mresetz__body(%Qubit* inttoptr (i64 1 to %Qubit*), %Result* inttoptr (i64 21 to %Result*))
  %var_191 = call i1 @__quantum__rt__read_result(%Result* inttoptr (i64 21 to %Result*))
  %var_192 = icmp eq i1 %var_191, false
  br i1 %var_192, label %block_64, label %block_65
block_64:
  %var_193 = fsub double %var_236, -0.007715636296885556
  br label %block_66
block_65:
  %var_194 = fadd double %var_236, -0.007715636296885556
  br label %block_66
block_66:
  %var_237 = phi double [%var_193, %block_64], [%var_194, %block_65]
  %var_195 = fsub double %var_237, -0.01588688760885283
  %var_197 = fmul double %var_195, -98.87376089446141
  %var_198 = fmul double -1.0, %var_197
  call void @__quantum__qis__h__body(%Qubit* inttoptr (i64 1 to %Qubit*))
  call void @__quantum__qis__rz__body(double %var_198, %Qubit* inttoptr (i64 1 to %Qubit*))
  call void @__quantum__qis__rz__body(double -49.436880447230706, %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__cx__body(%Qubit* inttoptr (i64 1 to %Qubit*), %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__rz__body(double 49.436880447230706, %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__cx__body(%Qubit* inttoptr (i64 1 to %Qubit*), %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__h__body(%Qubit* inttoptr (i64 1 to %Qubit*))
  call void @__quantum__qis__mresetz__body(%Qubit* inttoptr (i64 1 to %Qubit*), %Result* inttoptr (i64 22 to %Result*))
  %var_200 = call i1 @__quantum__rt__read_result(%Result* inttoptr (i64 22 to %Result*))
  %var_201 = icmp eq i1 %var_200, false
  br i1 %var_201, label %block_67, label %block_68
block_67:
  %var_202 = fsub double %var_237, -0.0061343945474072615
  br label %block_69
block_68:
  %var_203 = fadd double %var_237, -0.0061343945474072615
  br label %block_69
block_69:
  %var_238 = phi double [%var_202, %block_67], [%var_203, %block_68]
  %var_204 = fsub double %var_238, -0.012631030413182828
  %var_206 = fmul double %var_204, -124.36010961983581
  %var_207 = fmul double -1.0, %var_206
  call void @__quantum__qis__h__body(%Qubit* inttoptr (i64 1 to %Qubit*))
  call void @__quantum__qis__rz__body(double %var_207, %Qubit* inttoptr (i64 1 to %Qubit*))
  call void @__quantum__qis__rz__body(double -62.180054809917905, %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__cx__body(%Qubit* inttoptr (i64 1 to %Qubit*), %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__rz__body(double 62.180054809917905, %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__cx__body(%Qubit* inttoptr (i64 1 to %Qubit*), %Qubit* inttoptr (i64 0 to %Qubit*))
  call void @__quantum__qis__h__body(%Qubit* inttoptr (i64 1 to %Qubit*))
  call void @__quantum__qis__mresetz__body(%Qubit* inttoptr (i64 1 to %Qubit*), %Result* inttoptr (i64 23 to %Result*))
  %var_209 = call i1 @__quantum__rt__read_result(%Result* inttoptr (i64 23 to %Result*))
  %var_210 = icmp eq i1 %var_209, false
  br i1 %var_210, label %block_70, label %block_71
block_70:
  %var_211 = fsub double %var_238, -0.004877212327705201
  br label %block_72
block_71:
  %var_212 = fadd double %var_238, -0.004877212327705201
  br label %block_72
block_72:
  %var_239 = phi double [%var_211, %block_70], [%var_212, %block_71]
  %var_213 = fmul double -1.0, %var_239
  call void @__quantum__rt__double_record_output(double %var_213, i8* getelementptr inbounds ([3 x i8], [3 x i8]* @0, i32 0, i32 0))
  ret void
}

declare void @__quantum__qis__h__body(%Qubit*)

declare void @__quantum__qis__rz__body(double, %Qubit*)

declare void @__quantum__qis__cx__body(%Qubit*, %Qubit*)

declare void @__quantum__qis__mresetz__body(%Qubit*, %Result*) #1

declare i1 @__quantum__rt__read_result(%Result*)

declare void @__quantum__rt__double_record_output(double, i8*)

attributes #0 = { "entry_point" "output_labeling_schema" "qir_profiles"="adaptive_profile" "required_num_qubits"="2" "required_num_results"="24" }
attributes #1 = { "irreversible" }

; module flags

!llvm.module.flags = !{!0, !1, !2, !3, !4, !5}

!0 = !{i32 1, !"qir_major_version", i32 1}
!1 = !{i32 7, !"qir_minor_version", i32 0}
!2 = !{i32 1, !"dynamic_qubit_management", i1 false}
!3 = !{i32 1, !"dynamic_result_management", i1 false}
!4 = !{i32 1, !"int_computations", !"i64"}
!5 = !{i32 1, !"float_computations", !"f64"}