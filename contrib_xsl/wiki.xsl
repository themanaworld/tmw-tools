<?xml version="1.0"?>
<!-- Author: Reid
Copyright (C) 2016 Evol Online -->
<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    >

    <xsl:output method="text" indent="no"/>
    <xsl:strip-space elements="*"/>

    <xsl:template match="contributors">
        <xsl:apply-templates/>
    </xsl:template>

    <xsl:template match="evol">
        <xsl:text>^	Evol Online Contributors	^^&#xa;</xsl:text>
        <xsl:text>^	Nickname	^	Real Name / Email	^	Link	^&#xa;</xsl:text>
        <xsl:apply-templates/>
    </xsl:template>

    <xsl:template match="tmw-ufb">
        <xsl:text>^	Unknown Flying Bullet Contributors	^^&#xa;</xsl:text>
        <xsl:text>^	Nickname	^	Real Name / Email	^	Link	^&#xa;</xsl:text>
        <xsl:apply-templates/>
    </xsl:template>

    <xsl:template match="freesound">
        <xsl:text>^	Freesound Contributors	^^&#xa;</xsl:text>
        <xsl:text>^	Nickname	^	Real Name / Email	^	Link	^&#xa;</xsl:text>
        <xsl:apply-templates/>
    </xsl:template>

    <xsl:template match="other">
        <xsl:text>^	Related Community Contributors	^^&#xa;</xsl:text>
        <xsl:text>^	Name	^	Link	^&#xa;</xsl:text>

        <xsl:apply-templates select="community"/>
    </xsl:template>

    <xsl:template match="contributor">

        <xsl:text>|</xsl:text>
        <xsl:value-of select="@nick"/>

        <xsl:choose>
            <xsl:when test="@mailid">
                <xsl:text>	|[[mailto:</xsl:text>
                <xsl:value-of select="@mailid"/>
                <xsl:text>@</xsl:text>
                <xsl:value-of select="@mailserver"/>
                <xsl:text>| </xsl:text>
                <xsl:choose>
                    <xsl:when test="@name">
                        <xsl:value-of select="@name"/>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:value-of select="@nick"/>
                    </xsl:otherwise>
                </xsl:choose>
                <xsl:text>]]	|</xsl:text>
            </xsl:when>
            <xsl:otherwise>
                <xsl:text>	|</xsl:text>
                <xsl:choose>
                    <xsl:when test="@name">
                        <xsl:value-of select="@name"/>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:text>No Data</xsl:text>
                    </xsl:otherwise>
                </xsl:choose> 
                <xsl:text>	|</xsl:text>
            </xsl:otherwise>
        </xsl:choose>
        <xsl:choose>
            <xsl:when test="@page">
                <xsl:text>	</xsl:text>
                <xsl:value-of select="@page"/>
                <xsl:text>	|</xsl:text>
            </xsl:when>
            <xsl:otherwise>
                <xsl:text>	No Data	|</xsl:text>
            </xsl:otherwise>
        </xsl:choose>
        <xsl:text>&#xa;</xsl:text>
    </xsl:template>

    <xsl:template match="community">
        <xsl:text>|</xsl:text>
        <xsl:value-of select="@name"/>
        <xsl:text>	|[[</xsl:text>
        <xsl:value-of select="@site"/>
        <xsl:text>|</xsl:text>
        <xsl:value-of select="@name"/>
        <xsl:text>]]	|&#xa;</xsl:text>
    </xsl:template>

</xsl:stylesheet>
    
