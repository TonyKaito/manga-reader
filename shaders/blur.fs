#version 330

in vec2 fragTexCoord;
in vec4 fragColor;

uniform sampler2D texture0;
uniform vec4 colDiffuse;
uniform int kernelSize;
uniform vec2 texelSize;

out vec4 finalColor;

void main()
{
    int radius = max(kernelSize, 1) / 2;
    float sigma = max(float(radius) / 2.0, 0.5);
    float twoSigmaSquared = 2.0 * sigma * sigma;

    vec4 colorSum = vec4(0.0);
    float weightSum = 0.0;

    for (int y = -radius; y <= radius; ++y)
    {
        for (int x = -radius; x <= radius; ++x)
        {
            float distanceSquared = float(x * x + y * y);
            float weight = exp(-distanceSquared / twoSigmaSquared);

            vec2 sampleCoord = fragTexCoord + vec2(x, y) * texelSize;
			sampleCoord = clamp(sampleCoord, texelSize * 0.5, vec2(1.0) - texelSize * 0.5);
            colorSum += texture(texture0, sampleCoord) * weight;
            weightSum += weight;
        }
    }

	vec4 blurredColor = colorSum / weightSum;
    finalColor = vec4(blurredColor.rgb * 0.65, blurredColor.a);
}