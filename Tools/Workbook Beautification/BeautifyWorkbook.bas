Attribute VB_Name = "Module4"
Option Explicit

Sub BeautifyWorkbook()

    Dim WB As Workbook
    Dim WS As Worksheet
    Dim Rng As Range
    Dim c As Range
    Dim LastRow As Long
    Dim LastCol As Long

    Set WB = ActiveWorkbook

    Application.ScreenUpdating = False
    Application.EnableEvents = False
    Application.DisplayAlerts = False
    Application.Calculation = xlCalculationManual

    For Each WS In WB.Worksheets

        If Application.WorksheetFunction.CountA(WS.Cells) > 0 Then

            With WS

                LastRow = .Cells.Find(What:="*", _
                                      SearchOrder:=xlByRows, _
                                      SearchDirection:=xlPrevious).Row

                LastCol = .Cells.Find(What:="*", _
                                      SearchOrder:=xlByColumns, _
                                      SearchDirection:=xlPrevious).Column

                Set Rng = .Range(.Cells(1, 1), .Cells(LastRow, LastCol))

                '==============================
                ' AutoFit Columns & Rows
                '==============================
                .UsedRange.Columns.AutoFit
                .UsedRange.Rows.AutoFit

                '==============================
                ' Apply Borders
                '==============================
                Rng.Borders.LineStyle = xlNone

                With Rng.Borders
                    .LineStyle = xlContinuous
                    .Weight = xlThin
                    .Color = RGB(200, 200, 200)
                End With

                '==============================
                ' Header Formatting
                '==============================
                With .Range(.Cells(1, 1), .Cells(1, LastCol))
                    .Font.Bold = True
                    .Interior.Color = RGB(217, 217, 217)
                    .HorizontalAlignment = xlCenter
                    .VerticalAlignment = xlCenter
                End With

                '==============================
                ' Number Formatting
                '==============================
                For Each c In Rng

                    If IsNumeric(c.Value) And c.Value <> "" Then

                        If InStr(c.NumberFormat, "%") > 0 Then

                            'Percentage
                            c.NumberFormat = "0.00%"

                        ElseIf Not IsDate(c.Value) Then

                            'Numbers
                            c.NumberFormat = "#,##0.00"

                        End If

                    End If

                Next c

            End With

        End If

    Next WS

    Application.Calculation = xlCalculationAutomatic
    Application.ScreenUpdating = True
    Application.EnableEvents = True
    Application.DisplayAlerts = True

    MsgBox "Workbook formatting completed successfully.", vbInformation

End Sub

