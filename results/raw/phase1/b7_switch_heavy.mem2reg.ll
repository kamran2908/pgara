; ModuleID = 'results/raw/phase1/b7_switch_heavy.raw.ll'
source_filename = "benchmarks\\b7_switch_heavy.c"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.33.0"

; Function Attrs: noinline nounwind uwtable
define dso_local i32 @process_opcode(i32 noundef %0, i32 noundef %1, i32 noundef %2) #0 {
  switch i32 %0, label %19 [
    i32 0, label %4
    i32 1, label %6
    i32 2, label %8
    i32 3, label %10
    i32 4, label %13
    i32 5, label %15
    i32 6, label %17
  ]

4:                                                ; preds = %3
  %5 = add i32 %1, %2
  br label %20

6:                                                ; preds = %3
  %7 = sub i32 %1, %2
  br label %20

8:                                                ; preds = %3
  %9 = mul i32 %1, %2
  br label %20

10:                                               ; preds = %3
  %11 = add i32 %2, 1
  %12 = sdiv i32 %1, %11
  br label %20

13:                                               ; preds = %3
  %14 = and i32 %1, %2
  br label %20

15:                                               ; preds = %3
  %16 = or i32 %1, %2
  br label %20

17:                                               ; preds = %3
  %18 = xor i32 %1, %2
  br label %20

19:                                               ; preds = %3
  br label %20

20:                                               ; preds = %19, %17, %15, %13, %10, %8, %6, %4
  %.0 = phi i32 [ -1, %19 ], [ %5, %4 ], [ %7, %6 ], [ %9, %8 ], [ %12, %10 ], [ %14, %13 ], [ %16, %15 ], [ %18, %17 ]
  ret i32 %.0
}

attributes #0 = { noinline nounwind uwtable "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }

!llvm.dbg.cu = !{!0}
!llvm.module.flags = !{!2, !3, !4, !5}
!llvm.ident = !{!6}

!0 = distinct !DICompileUnit(language: DW_LANG_C11, file: !1, producer: "clang version 23.1.3 (https://github.com/llvm/llvm-project 0d261d1ca552c95a8f007e061c787ac7132fbcbc)", isOptimized: false, runtimeVersion: 0, emissionKind: NoDebug, splitDebugInlining: false, nameTableKind: None)
!1 = !DIFile(filename: "benchmarks\\b7_switch_heavy.c", directory: "D:\\Sem 5 Projects\\PGARA")
!2 = !{i32 2, !"Debug Info Version", i32 3}
!3 = !{i32 8, !"PIC Level", i32 2}
!4 = !{i32 7, !"uwtable", i32 2}
!5 = !{i32 1, !"MaxTLSAlign", i32 65536}
!6 = !{!"clang version 23.1.3 (https://github.com/llvm/llvm-project 0d261d1ca552c95a8f007e061c787ac7132fbcbc)"}
