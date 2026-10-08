; ModuleID = 'benchmarks\b7_switch_heavy.c'
source_filename = "benchmarks\\b7_switch_heavy.c"
target datalayout = "e-m:w-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-windows-msvc19.33.0"

; Function Attrs: noinline nounwind uwtable
define dso_local i32 @process_opcode(i32 noundef %0, i32 noundef %1, i32 noundef %2) #0 {
  %4 = alloca i32, align 4
  %5 = alloca i32, align 4
  %6 = alloca i32, align 4
  %7 = alloca i32, align 4
  store i32 %2, ptr %4, align 4
  store i32 %1, ptr %5, align 4
  store i32 %0, ptr %6, align 4
  store i32 0, ptr %7, align 4
  %8 = load i32, ptr %6, align 4
  switch i32 %8, label %38 [
    i32 0, label %9
    i32 1, label %13
    i32 2, label %17
    i32 3, label %21
    i32 4, label %26
    i32 5, label %30
    i32 6, label %34
  ]

9:                                                ; preds = %3
  %10 = load i32, ptr %5, align 4
  %11 = load i32, ptr %4, align 4
  %12 = add i32 %10, %11
  store i32 %12, ptr %7, align 4
  br label %39

13:                                               ; preds = %3
  %14 = load i32, ptr %5, align 4
  %15 = load i32, ptr %4, align 4
  %16 = sub i32 %14, %15
  store i32 %16, ptr %7, align 4
  br label %39

17:                                               ; preds = %3
  %18 = load i32, ptr %5, align 4
  %19 = load i32, ptr %4, align 4
  %20 = mul i32 %18, %19
  store i32 %20, ptr %7, align 4
  br label %39

21:                                               ; preds = %3
  %22 = load i32, ptr %5, align 4
  %23 = load i32, ptr %4, align 4
  %24 = add i32 %23, 1
  %25 = sdiv i32 %22, %24
  store i32 %25, ptr %7, align 4
  br label %39

26:                                               ; preds = %3
  %27 = load i32, ptr %5, align 4
  %28 = load i32, ptr %4, align 4
  %29 = and i32 %27, %28
  store i32 %29, ptr %7, align 4
  br label %39

30:                                               ; preds = %3
  %31 = load i32, ptr %5, align 4
  %32 = load i32, ptr %4, align 4
  %33 = or i32 %31, %32
  store i32 %33, ptr %7, align 4
  br label %39

34:                                               ; preds = %3
  %35 = load i32, ptr %5, align 4
  %36 = load i32, ptr %4, align 4
  %37 = xor i32 %35, %36
  store i32 %37, ptr %7, align 4
  br label %39

38:                                               ; preds = %3
  store i32 -1, ptr %7, align 4
  br label %39

39:                                               ; preds = %38, %34, %30, %26, %21, %17, %13, %9
  %40 = load i32, ptr %7, align 4
  ret i32 %40
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
