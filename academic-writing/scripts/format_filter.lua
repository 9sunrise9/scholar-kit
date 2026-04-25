local filter = {}

function Math(elem)
  if elem.mathtype == "InlineMath" then
    return elem
  end
  return pandoc.Math({mathmode = "DisplayMath"}, elem.text)
end

function Header(elem)
  return elem
end

function CodeBlock(elem)
  return elem
end

return filter
