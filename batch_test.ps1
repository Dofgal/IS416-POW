$mal_num = 2

for ($mal_num; $mal_num -lt 9; $mal_num++)
{   
    $cnt = 10
    Write-Host "节点总数: 20, 恶意节点数量: $mal_num"
    while ($cnt -gt 0)
    {
        python batch_test.py 20 $mal_num
        $cnt --
    }
    Write-Host "`n"
}